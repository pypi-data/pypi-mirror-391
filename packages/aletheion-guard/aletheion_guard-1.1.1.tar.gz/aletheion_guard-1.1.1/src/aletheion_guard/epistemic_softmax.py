# PROPRIETARY AND CONFIDENTIAL
# Copyright (c) 2024-2025 AletheionAGI
# Unauthorized copying prohibited
#
# LEVEL 3 PROPRIETARY ALGORITHM
# This file contains proprietary epistemic softmax implementations
# that are confidential and not covered by AGPL-3.0

"""
Epistemic Softmax - Core component from aletheion-llm architecture.

This module implements epistemic softmax, replacing traditional softmax with
uncertainty-aware probability distributions. This is a key innovation from the
aletheion-llm project, adapted for the AletheionGuard auditor architecture.

Mathematical formulation:
    Traditional softmax: p_i = exp(z_i / τ) / Σ exp(z_j / τ)
    Epistemic softmax: p_i = exp(z_i / τ_adaptive) / Σ exp(z_j / τ_adaptive)

    where τ_adaptive = τ_base * (1 + Q1 + Q2)

    This increases temperature (flattens distribution) when uncertainty is high,
    and decreases temperature (sharpens distribution) when uncertainty is low.

References:
    - aletheion-llm: https://github.com/AletheionAGI/aletheion-llm
    - "How to Solve Skynet: A Pyramidal Law for Epistemic Equilibrium"
"""

from typing import Optional, Tuple, Dict, Union
import torch
import torch.nn as nn
import torch.nn.functional as F


class LocalUncertaintyGate(nn.Module):
    """
    Local Uncertainty Gate (Q₁) - from aletheion-llm.

    Captures token-level uncertainty in predictions. This is similar to
    AletheionGuard's Q1Gate but designed for integration with epistemic softmax.

    This gate estimates aleatoric (irreducible) uncertainty at the local level,
    answering: "How uncertain would we be even with infinite data?"
    """

    def __init__(
        self,
        d_model: int = 384,
        hidden_dim: int = 256,
        dropout: float = 0.1
    ):
        """
        Initialize Local Uncertainty Gate.

        Args:
            d_model: Model dimension (embedding size)
            hidden_dim: Hidden layer dimension
            dropout: Dropout probability for regularization
        """
        super().__init__()

        self.d_model = d_model
        self.hidden_dim = hidden_dim

        # Network architecture
        self.network = nn.Sequential(
            nn.Linear(d_model, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Q₁ ∈ [0, 1]
        )

        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Estimate local (aleatoric) uncertainty.

        Args:
            embeddings: Input embeddings, shape (batch_size, d_model) or (d_model,)

        Returns:
            Q₁ values ∈ [0, 1], shape (batch_size, 1) or (1,)
        """
        # Handle single sample
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        q1 = self.network(embeddings)

        # Remove batch dimension for single sample
        if single_sample:
            q1 = q1.squeeze(0)

        return q1


class CrossContextGate(nn.Module):
    """
    Cross-Context Gate (Q₂) - from aletheion-llm.

    Models semantic coherence across context. This captures epistemic
    (reducible) uncertainty - how much the model doesn't know.

    This gate is conditioned on Q₁ to provide better calibration,
    answering: "Given the local uncertainty (Q₁), how uncertain is
    the model about its knowledge?"
    """

    def __init__(
        self,
        d_model: int = 384,
        n_heads: int = 4,
        hidden_dim: int = 256,
        dropout: float = 0.1
    ):
        """
        Initialize Cross-Context Gate.

        Args:
            d_model: Model dimension (embedding size)
            n_heads: Number of attention heads (for future attention mechanism)
            hidden_dim: Hidden layer dimension
            dropout: Dropout probability for regularization
        """
        super().__init__()

        self.d_model = d_model
        self.n_heads = n_heads
        self.hidden_dim = hidden_dim

        # Network architecture: conditioned on Q₁
        # Input: [embeddings (d_model), q1 (1)] = d_model + 1
        self.network = nn.Sequential(
            nn.Linear(d_model + 1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Q₂ ∈ [0, 1]
        )

        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(
        self,
        embeddings: torch.Tensor,
        q1: torch.Tensor
    ) -> torch.Tensor:
        """
        Estimate cross-context (epistemic) uncertainty.

        Args:
            embeddings: Input embeddings, shape (batch_size, d_model) or (d_model,)
            q1: Local uncertainty (Q₁), shape (batch_size, 1) or (1,)

        Returns:
            Q₂ values ∈ [0, 1], shape (batch_size, 1) or (1,)
        """
        # Handle single sample
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        # Ensure q1 has correct shape
        if q1.dim() == 0:
            q1 = q1.unsqueeze(0).unsqueeze(0)
        elif q1.dim() == 1:
            q1 = q1.unsqueeze(1)

        # Concatenate embeddings with Q₁ for conditioning
        x = torch.cat([embeddings, q1], dim=-1)

        q2 = self.network(x)

        # Remove batch dimension for single sample
        if single_sample:
            q2 = q2.squeeze(0)

        return q2


def epistemic_softmax(
    logits: torch.Tensor,
    context: Optional[torch.Tensor] = None,
    q1_gate: Optional[LocalUncertaintyGate] = None,
    q2_gate: Optional[CrossContextGate] = None,
    base_temperature: float = 1.0,
    confidence_threshold: float = 0.7,
    return_uncertainty: bool = True
) -> Union[torch.Tensor, Tuple[torch.Tensor, Dict[str, torch.Tensor]]]:
    """
    Epistemic Softmax - uncertainty-aware probability distribution.

    This is the core innovation from aletheion-llm, replacing traditional
    softmax with an uncertainty-modulated version that:

    1. Estimates Q₁ (aleatoric) and Q₂ (epistemic) uncertainty
    2. Adapts temperature based on total uncertainty
    3. Returns calibrated probabilities that reflect model confidence

    Mathematical formulation:
        τ_adaptive = τ_base * (1 + Q₁ + Q₂)
        p_i = exp(z_i / τ_adaptive) / Σ exp(z_j / τ_adaptive)

    High uncertainty → High temperature → Flatter distribution
    Low uncertainty → Low temperature → Sharper distribution

    Args:
        logits: Logit values, shape (batch_size, num_classes) or (num_classes,)
        context: Context embeddings, shape (batch_size, d_model) or (d_model,).
                 If None, uses logits as proxy for embeddings.
        q1_gate: Local uncertainty gate (Q₁). If None, creates default.
        q2_gate: Cross-context uncertainty gate (Q₂). If None, creates default.
        base_temperature: Base temperature τ_base (default: 1.0)
        confidence_threshold: Threshold for high-confidence predictions (default: 0.7)
        return_uncertainty: If True, returns (probs, uncertainty_dict)

    Returns:
        If return_uncertainty=False:
            probs: Epistemic softmax probabilities
        If return_uncertainty=True:
            (probs, uncertainty_dict) where uncertainty_dict contains:
                - q1: Aleatoric uncertainty
                - q2: Epistemic uncertainty
                - total_uncertainty: sqrt(Q₁² + Q₂²)
                - temperature: Adaptive temperature used
                - height: Epistemic height (1 - total_uncertainty)
                - confidence: Max probability value

    Example:
        >>> logits = torch.tensor([2.0, 1.0, 0.5])
        >>> probs, uncertainty = epistemic_softmax(logits, return_uncertainty=True)
        >>> print(f"Q1: {uncertainty['q1']:.3f}, Q2: {uncertainty['q2']:.3f}")
        >>> print(f"Probs: {probs}")
    """
    # Handle single sample (add batch dimension)
    if logits.dim() == 1:
        logits = logits.unsqueeze(0)
        single_sample = True
    else:
        single_sample = False

    batch_size = logits.size(0)

    # Use logits as embeddings if context not provided
    # (This is a simplification - in aletheion-llm, context comes from hidden states)
    if context is None:
        # Use mean-pooled logits as embedding proxy
        context = logits.mean(dim=-1, keepdim=True).expand(-1, 384)
        # Normalize to [0, 1] range
        context = torch.sigmoid(context)

    # Ensure context has correct shape
    if context.dim() == 1:
        context = context.unsqueeze(0)

    # Create default gates if not provided
    if q1_gate is None:
        q1_gate = LocalUncertaintyGate(d_model=context.size(-1))
        q1_gate.eval()  # Use in eval mode (no dropout)

    if q2_gate is None:
        q2_gate = CrossContextGate(d_model=context.size(-1))
        q2_gate.eval()

    # Estimate uncertainties
    with torch.no_grad() if not q1_gate.training else torch.enable_grad():
        q1 = q1_gate(context)  # Aleatoric (local) uncertainty
        q2 = q2_gate(context, q1)  # Epistemic (cross-context) uncertainty

    # Ensure q1, q2 are scalars or have correct shape
    if q1.dim() > 1:
        q1 = q1.squeeze(-1)
    if q2.dim() > 1:
        q2 = q2.squeeze(-1)

    # Compute adaptive temperature
    # High uncertainty → High temperature → Flatter distribution
    # τ_adaptive = τ_base * (1 + Q₁ + Q₂)
    temperature_scale = 1.0 + q1 + q2
    if temperature_scale.dim() == 0:
        temperature_scale = temperature_scale.unsqueeze(0)

    adaptive_temperature = base_temperature * temperature_scale

    # Ensure adaptive_temperature has correct shape for broadcasting
    if adaptive_temperature.size(0) == batch_size:
        adaptive_temperature = adaptive_temperature.unsqueeze(-1)

    # Apply epistemic softmax with adaptive temperature
    scaled_logits = logits / adaptive_temperature
    probs = F.softmax(scaled_logits, dim=-1)

    # Remove batch dimension for single sample
    if single_sample:
        probs = probs.squeeze(0)
        q1 = q1.squeeze(0) if q1.dim() > 0 else q1
        q2 = q2.squeeze(0) if q2.dim() > 0 else q2
        adaptive_temperature = adaptive_temperature.squeeze(0)

    if not return_uncertainty:
        return probs

    # Compute additional uncertainty metrics
    total_uncertainty = torch.sqrt(q1**2 + q2**2)
    height = 1.0 - total_uncertainty
    confidence = probs.max() if single_sample else probs.max(dim=-1)[0]

    uncertainty_dict = {
        "q1": q1,
        "q2": q2,
        "total_uncertainty": total_uncertainty,
        "temperature": adaptive_temperature,
        "height": height,
        "confidence": confidence,
        "is_high_confidence": confidence > confidence_threshold
    }

    return probs, uncertainty_dict


class EpistemicSoftmaxLayer(nn.Module):
    """
    Epistemic Softmax as a PyTorch module.

    This wraps the epistemic_softmax function as a trainable layer that
    can be integrated into neural architectures.

    Example usage:
        >>> layer = EpistemicSoftmaxLayer(d_model=384, base_temperature=1.0)
        >>> logits = torch.randn(32, 10)  # batch_size=32, num_classes=10
        >>> context = torch.randn(32, 384)
        >>> probs, uncertainty = layer(logits, context)
    """

    def __init__(
        self,
        d_model: int = 384,
        base_temperature: float = 1.0,
        confidence_threshold: float = 0.7,
        dropout: float = 0.1
    ):
        """
        Initialize Epistemic Softmax Layer.

        Args:
            d_model: Model dimension (embedding size)
            base_temperature: Base temperature for softmax
            confidence_threshold: Threshold for high-confidence predictions
            dropout: Dropout probability for Q₁/Q₂ gates
        """
        super().__init__()

        self.d_model = d_model
        self.base_temperature = base_temperature
        self.confidence_threshold = confidence_threshold

        # Create Q₁ and Q₂ gates
        self.q1_gate = LocalUncertaintyGate(
            d_model=d_model,
            dropout=dropout
        )

        self.q2_gate = CrossContextGate(
            d_model=d_model,
            dropout=dropout
        )

    def forward(
        self,
        logits: torch.Tensor,
        context: Optional[torch.Tensor] = None,
        return_uncertainty: bool = True
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, Dict[str, torch.Tensor]]]:
        """
        Apply epistemic softmax.

        Args:
            logits: Logit values
            context: Context embeddings (optional)
            return_uncertainty: Whether to return uncertainty metrics

        Returns:
            Probabilities and optionally uncertainty metrics
        """
        return epistemic_softmax(
            logits=logits,
            context=context,
            q1_gate=self.q1_gate,
            q2_gate=self.q2_gate,
            base_temperature=self.base_temperature,
            confidence_threshold=self.confidence_threshold,
            return_uncertainty=return_uncertainty
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def compare_softmax(
    logits: torch.Tensor,
    context: Optional[torch.Tensor] = None,
    temperature: float = 1.0
) -> Dict[str, torch.Tensor]:
    """
    Compare traditional softmax vs epistemic softmax.

    Args:
        logits: Logit values
        context: Context embeddings (optional)
        temperature: Temperature for traditional softmax

    Returns:
        Dictionary with comparison metrics:
            - traditional_probs: Standard softmax probabilities
            - epistemic_probs: Epistemic softmax probabilities
            - kl_divergence: KL divergence between the two
            - uncertainty: Uncertainty metrics from epistemic softmax
    """
    # Traditional softmax
    traditional_probs = F.softmax(logits / temperature, dim=-1)

    # Epistemic softmax
    epistemic_probs, uncertainty = epistemic_softmax(
        logits=logits,
        context=context,
        base_temperature=temperature,
        return_uncertainty=True
    )

    # Compute KL divergence: KL(epistemic || traditional)
    kl_div = F.kl_div(
        epistemic_probs.log(),
        traditional_probs,
        reduction='batchmean'
    )

    return {
        "traditional_probs": traditional_probs,
        "epistemic_probs": epistemic_probs,
        "kl_divergence": kl_div,
        "uncertainty": uncertainty
    }


def apply_epistemic_sampling(
    logits: torch.Tensor,
    context: Optional[torch.Tensor] = None,
    base_temperature: float = 1.0,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    Sample from epistemic softmax distribution with optional top-k/top-p filtering.

    This is useful for text generation where you want uncertainty-aware sampling.

    Args:
        logits: Logit values, shape (batch_size, vocab_size) or (vocab_size,)
        context: Context embeddings (optional)
        base_temperature: Base temperature
        top_k: If set, only sample from top k tokens
        top_p: If set, use nucleus sampling

    Returns:
        (sampled_tokens, uncertainty_dict)
    """
    # Get epistemic probabilities
    probs, uncertainty = epistemic_softmax(
        logits=logits,
        context=context,
        base_temperature=base_temperature,
        return_uncertainty=True
    )

    # Apply top-k filtering if requested
    if top_k is not None:
        top_k_probs, top_k_indices = probs.topk(top_k, dim=-1)
        # Create filtered probs tensor
        filtered_probs = torch.zeros_like(probs)
        filtered_probs.scatter_(-1, top_k_indices, top_k_probs)
        # Renormalize
        probs = filtered_probs / filtered_probs.sum(dim=-1, keepdim=True)

    # Apply top-p (nucleus) filtering if requested
    if top_p is not None:
        sorted_probs, sorted_indices = probs.sort(descending=True, dim=-1)
        cumulative_probs = sorted_probs.cumsum(dim=-1)

        # Remove tokens with cumulative probability above threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Keep at least one token
        sorted_indices_to_remove[..., 0] = False

        # Scatter back to original indices
        indices_to_remove = sorted_indices_to_remove.scatter(
            -1, sorted_indices, sorted_indices_to_remove
        )
        probs = probs.masked_fill(indices_to_remove, 0.0)
        # Renormalize
        probs = probs / probs.sum(dim=-1, keepdim=True)

    # Sample from the distribution
    sampled_tokens = torch.multinomial(probs, num_samples=1)

    return sampled_tokens, uncertainty


# ============================================================================
# INTEGRATION WITH EXISTING Q1/Q2 GATES
# ============================================================================

def create_epistemic_softmax_from_gates(
    q1_gate: nn.Module,
    q2_gate: nn.Module,
    base_temperature: float = 1.0
) -> EpistemicSoftmaxLayer:
    """
    Create an EpistemicSoftmaxLayer using existing Q1/Q2 gates.

    This allows integration with AletheionGuard's existing Q1Gate and Q2Gate.

    Args:
        q1_gate: Existing Q1Gate (or compatible LocalUncertaintyGate)
        q2_gate: Existing Q2Gate (or compatible CrossContextGate)
        base_temperature: Base temperature

    Returns:
        EpistemicSoftmaxLayer instance with shared gates
    """
    layer = EpistemicSoftmaxLayer(
        d_model=q1_gate.input_dim,
        base_temperature=base_temperature
    )

    # Replace gates with existing trained gates
    # Note: This assumes the existing gates have compatible architecture
    layer.q1_gate = q1_gate
    layer.q2_gate = q2_gate

    return layer
