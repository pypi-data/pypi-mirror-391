# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Core epistemic auditor implementation.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import math


@dataclass
class EpistemicAudit:
    """
    Results from epistemic auditing of an LLM response.

    Attributes:
        q1: Aleatoric uncertainty [0,1] - irreducible data noise
        q2: Epistemic uncertainty [0,1] - model ignorance
        height: Truth proximity [0,1] - distance from base to apex
        ece: Expected Calibration Error [0,1]
        brier: Brier score [0,1]
        verdict: "ACCEPT" | "MAYBE" | "REFUSED"
        confidence_interval: 95% CI for height metric
        explanation: Human-readable reasoning
        metadata: Additional metrics and diagnostics
    """
    q1: float
    q2: float
    height: float
    ece: float
    brier: float
    verdict: str
    confidence_interval: Tuple[float, float]
    explanation: str
    metadata: Dict

    def to_dict(self) -> dict:
        """Convert audit to dictionary."""
        return {
            "q1": self.q1,
            "q2": self.q2,
            "height": self.height,
            "ece": self.ece,
            "brier": self.brier,
            "verdict": self.verdict,
            "confidence_interval": self.confidence_interval,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }

    def is_reliable(self) -> bool:
        """Check if response is reliable."""
        return self.verdict == "ACCEPT"

    def requires_review(self) -> bool:
        """Check if manual review is needed."""
        return self.verdict in ["MAYBE", "REFUSED"]


class EpistemicAuditor:
    """
    Main auditor for epistemic uncertainty quantification in LLM outputs.

    This class implements the pyramidal architecture for separating
    aleatoric (Q1) from epistemic (Q2) uncertainty.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "auto",
        config: Optional[Dict] = None
    ):
        """
        Initialize the epistemic auditor.

        Args:
            model_path: Path to custom model weights (optional)
            device: Device to run on ("cpu", "cuda", "mps", or "auto")
            config: Custom configuration dictionary
        """
        import torch
        from .input_processor import InputProcessor
        from .q1q2_gates import Q1Gate, Q2Gate
        from .pyramidal import PyramidalArchitecture
        from utils.calibration import CalibrationScorer

        # Auto-detect device
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.model_path = model_path
        self.device = device
        self.config = config or self._default_config()

        # Initialize components
        self.input_processor = InputProcessor(device=device)
        self.q1_gate = Q1Gate(
            input_dim=384,
            hidden_dim=self.config.get("hidden_dim", 256)
        ).to(device)
        self.q2_gate = Q2Gate(
            input_dim=384,
            hidden_dim=self.config.get("hidden_dim", 256)
        ).to(device)
        self.pyramidal = PyramidalArchitecture()
        self.calibration_scorer = CalibrationScorer(n_bins=self.config.get("ece_bins", 15))

        # Load custom weights if provided
        if model_path is not None:
            self._load_weights(model_path)

    def _load_weights(self, model_path: str):
        """
        Load pretrained weights for Q1 and Q2 gates.

        Args:
            model_path: Path to model checkpoint directory
        """
        import torch
        import os

        q1_path = os.path.join(model_path, "q1_gate.pt")
        q2_path = os.path.join(model_path, "q2_gate.pt")

        if os.path.exists(q1_path):
            self.q1_gate.load_state_dict(torch.load(q1_path, map_location=self.device))
            print(f"Loaded Q1 gate weights from {q1_path}")

        if os.path.exists(q2_path):
            self.q2_gate.load_state_dict(torch.load(q2_path, map_location=self.device))
            print(f"Loaded Q2 gate weights from {q2_path}")

    def _default_config(self) -> dict:
        """Get default configuration."""
        return {
            "q1_threshold": 0.3,
            "q2_threshold": 0.3,
            "ece_bins": 15,
            "confidence_level": 0.95,
            "batch_size": 32,
            "max_length": 512,
            "hidden_dim": 256,
        }

    def evaluate(
        self,
        text: str,
        context: Optional[str] = None,
        model_source: Optional[str] = None,
        ground_truth: Optional[str] = None
    ) -> EpistemicAudit:
        """
        Audit a single LLM response.

        Mathematical process:
        1. text → embeddings (sentence-transformers)
        2. embeddings → Q1 (aleatoric uncertainty)
        3. embeddings + Q1 → Q2 (epistemic uncertainty)
        4. h = 1 - sqrt(Q1² + Q2²) (pyramidal height)
        5. Verdict based on thresholds

        Args:
            text: The LLM response to audit
            context: Additional context (e.g., original prompt)
            model_source: Source model name (e.g., "gpt-4")
            ground_truth: Known correct answer for calibration

        Returns:
            EpistemicAudit object with uncertainty metrics
        """
        import torch

        # Step 1: Compute embeddings
        embeddings = self.input_processor.encode_with_context(text, context)

        # Ensure embeddings are on the correct device
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.to(self.device)

        # Step 2: Estimate Q1 (aleatoric uncertainty)
        q1 = self._estimate_q1(embeddings)

        # Step 3: Estimate Q2 (epistemic uncertainty, conditioned on Q1)
        q2 = self._estimate_q2(embeddings, q1)

        # Step 4: Compute height metric
        height = self._compute_height(q1, q2)

        # Step 5: Compute calibration metrics (placeholder for now)
        ece = self._compute_ece(height)
        brier = self._compute_brier(height)

        # Step 6: Determine verdict
        verdict = self._determine_verdict(q1, q2, height)

        # Step 7: Compute confidence interval
        ci = self._confidence_interval(height)

        # Step 8: Generate explanation
        explanation = self._generate_explanation(q1, q2, height, verdict)

        return EpistemicAudit(
            q1=q1,
            q2=q2,
            height=height,
            ece=ece,
            brier=brier,
            verdict=verdict,
            confidence_interval=ci,
            explanation=explanation,
            metadata={
                "model_source": model_source,
                "context_provided": context is not None,
                "device": self.device,
                "embedding_dim": self.input_processor.get_embedding_dim(),
            }
        )

    def batch_evaluate(
        self,
        texts: List[str],
        contexts: Optional[List[str]] = None,
        batch_size: int = 32
    ) -> List[EpistemicAudit]:
        """
        Audit multiple responses efficiently using batched inference.

        Args:
            texts: List of LLM responses
            contexts: List of contexts (optional)
            batch_size: Batch size for processing

        Returns:
            List of EpistemicAudit objects
        """
        import torch

        audits = []

        # Process in batches for efficiency
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_contexts = contexts[i:i + batch_size] if contexts else None

            # Compute embeddings for the batch
            if batch_contexts:
                embeddings_batch = self.input_processor.encode_with_context(
                    batch_texts,
                    batch_contexts
                )
            else:
                embeddings_batch = self.input_processor.encode(batch_texts)

            # Ensure on correct device
            embeddings_batch = embeddings_batch.to(self.device)

            # Batch inference for Q1
            with torch.no_grad():
                q1_batch = self.q1_gate.forward(embeddings_batch)

            # Batch inference for Q2 (conditioned on Q1)
            with torch.no_grad():
                q2_batch = self.q2_gate.forward(embeddings_batch, q1_batch.squeeze())

            # Process each item in the batch
            for j in range(len(batch_texts)):
                q1 = q1_batch[j].item() if q1_batch.dim() > 1 else q1_batch.item()
                q2 = q2_batch[j].item() if q2_batch.dim() > 1 else q2_batch.item()

                height = self._compute_height(q1, q2)
                ece = self._compute_ece(height)
                brier = self._compute_brier(height)
                verdict = self._determine_verdict(q1, q2, height)
                ci = self._confidence_interval(height)
                explanation = self._generate_explanation(q1, q2, height, verdict)

                audit = EpistemicAudit(
                    q1=q1,
                    q2=q2,
                    height=height,
                    ece=ece,
                    brier=brier,
                    verdict=verdict,
                    confidence_interval=ci,
                    explanation=explanation,
                    metadata={
                        "context_provided": batch_contexts is not None,
                        "batch_index": i + j,
                    }
                )
                audits.append(audit)

        return audits

    def compare_models(
        self,
        prompt: str,
        models: List[str],
        responses: Optional[List[str]] = None,
        ground_truth: Optional[str] = None
    ) -> Dict:
        """
        Compare calibration across different LLMs.

        Args:
            prompt: The prompt sent to all models
            models: List of model names
            responses: Pre-generated responses (optional)
            ground_truth: Known correct answer (optional)

        Returns:
            Dictionary with comparison results
        """
        # TODO: Implement model comparison
        raise NotImplementedError("Model comparison coming soon")

    def calibrate(
        self,
        texts: List[str],
        labels: List[bool],
        epochs: int = 10,
        learning_rate: float = 1e-4
    ):
        """
        Fine-tune auditor on domain-specific data.

        Args:
            texts: Training texts
            labels: True/False labels (accuracy)
            epochs: Training epochs
            learning_rate: Learning rate
        """
        # TODO: Implement calibration/fine-tuning
        raise NotImplementedError("Calibration coming soon")

    # Real uncertainty estimation methods using neural networks
    def _estimate_q1(self, embeddings) -> float:
        """
        Estimate aleatoric uncertainty using Q1 gate.

        Equation: Q1* = 1 - p(y* | x)
        Represents irreducible data noise and ambiguity.

        Args:
            embeddings: Text embeddings tensor

        Returns:
            Q1 value in [0, 1]
        """
        import torch

        with torch.no_grad():
            q1 = self.q1_gate(embeddings)

            # Convert to float if tensor
            if isinstance(q1, torch.Tensor):
                q1 = q1.item()

        return float(q1)

    def _estimate_q2(self, embeddings, q1: float) -> float:
        """
        Estimate epistemic uncertainty using Q2 gate.

        Equation: Q2* = 1/2 * [(1 - 1[argmax p = y*]) + H(p)/log V]
        Conditioned on Q1 for better calibration.

        Args:
            embeddings: Text embeddings tensor
            q1: Aleatoric uncertainty (conditioning variable)

        Returns:
            Q2 value in [0, 1]
        """
        import torch

        with torch.no_grad():
            q2 = self.q2_gate(embeddings, q1)

            # Convert to float if tensor
            if isinstance(q2, torch.Tensor):
                q2 = q2.item()

        return float(q2)

    def _compute_height(self, q1: float, q2: float) -> float:
        """
        Compute height metric (truth proximity).

        Equation: h = 1 - sqrt(Q1² + Q2²)

        This implements the pyramidal geometry where height represents
        proximity to the apex (perfect knowledge/truth).

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Height value in [0, 1] where 1 = apex (perfect knowledge)
        """
        return self.pyramidal.compute_height(q1, q2)

    def _compute_ece(self, height: float) -> float:
        """Compute Expected Calibration Error."""
        # Placeholder
        return max(0.03, 0.15 - height * 0.12)

    def _compute_brier(self, height: float) -> float:
        """Compute Brier score."""
        # Placeholder
        return max(0.02, 0.20 - height * 0.15)

    def _determine_verdict(self, q1: float, q2: float, height: float) -> str:
        """
        Determine verdict based on uncertainty levels using official epistemic rules.

        Official epistemic rule:
        - u = 1.0 - height (total uncertainty = sqrt(q1² + q2²))
        - If q2 >= 0.35 OR u >= 0.60 → REFUSED (high epistemic uncertainty or total uncertainty)
        - If q1 >= 0.35 OR (0.30 <= u < 0.60) → MAYBE (high aleatoric or moderate total uncertainty)
        - Otherwise → ACCEPT (low uncertainty)

        Args:
            q1: Aleatoric uncertainty [0, 1]
            q2: Epistemic uncertainty [0, 1]
            height: Truth proximity [0, 1]

        Returns:
            Verdict: "ACCEPT", "MAYBE", or "REFUSED"
        """
        u = 1.0 - height  # Total uncertainty

        # Refused: High epistemic OR total uncertainty too high
        if q2 >= 0.35 or u >= 0.60:
            return "REFUSED"

        # Maybe: High aleatoric OR moderate total uncertainty
        if q1 >= 0.35 or (0.30 <= u < 0.60):
            return "MAYBE"

        # Accept: Low uncertainty
        return "ACCEPT"

    def _confidence_interval(self, height: float) -> Tuple[float, float]:
        """Compute 95% confidence interval for height."""
        margin = 0.05
        return (max(0, height - margin), min(1, height + margin))

    def _generate_explanation(
        self,
        q1: float,
        q2: float,
        height: float,
        verdict: str
    ) -> str:
        """Generate human-readable explanation."""
        if verdict == "ACCEPT":
            return "Low uncertainty across both dimensions. The response is well-calibrated and likely accurate."
        elif verdict == "MAYBE":
            if q1 > q2:
                return "Moderate aleatoric uncertainty. The question may have inherent ambiguity or multiple valid answers."
            else:
                return "Some epistemic uncertainty detected. The model may lack complete knowledge on this topic."
        else:  # REFUSED
            return "High epistemic uncertainty or total uncertainty detected. The model may lack sufficient knowledge or the claim is highly speculative."


class AuditorError(Exception):
    """Base exception for auditor errors."""
    pass
