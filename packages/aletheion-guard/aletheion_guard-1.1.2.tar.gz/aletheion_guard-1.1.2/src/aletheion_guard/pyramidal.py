# PROPRIETARY AND CONFIDENTIAL
# Copyright (c) 2024-2025 AletheionAGI
# Unauthorized copying prohibited
#
# LEVEL 3 PROPRIETARY ARCHITECTURE
# This file contains proprietary pyramidal architecture implementations
# that are confidential and not covered by AGPL-3.0

"""
Pyramidal architecture for epistemic equilibrium.

Implements the hierarchical model from "How to Solve Skynet" paper.

Architecture Levels (aligned with aletheion-llm):
- Level 1: pyramidal_q1q2 - Q1/Q2 gates + Height Gate + Base Forces (IMPLEMENTED HERE)
- Level 2: Level 1 + Attention Head mechanism (planned)
- Level 3: Full fractal with meta-epistemic uncertainty (planned)

Note: The basic Q1/Q2-only implementation (without Height/Base Forces) is available
in train_basic.py for reference, but is not recommended for production use.
"""

import math
from typing import Tuple, Optional, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F


class PyramidalArchitecture:
    """
    Pyramidal architecture for epistemic uncertainty quantification.

    The pyramid represents knowledge as a hierarchy:
    - Base: Maximum uncertainty (ignorance)
    - Q1 Layer: Aleatoric uncertainty
    - Q2 Layer: Epistemic uncertainty
    - Apex: Perfect knowledge (truth)
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize pyramidal architecture.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def compute_height(self, q1: float, q2: float) -> float:
        """
        Compute height metric (proximity to truth).

        Height = 1 - sqrt(Q1² + Q2²)

        Args:
            q1: Aleatoric uncertainty [0, 1]
            q2: Epistemic uncertainty [0, 1]

        Returns:
            Height value [0, 1] where 1 = apex (perfect knowledge)
        """
        uncertainty_magnitude = math.sqrt(q1**2 + q2**2)
        height = 1.0 - uncertainty_magnitude
        return max(0.0, min(1.0, height))  # Clamp to [0, 1]

    def compute_position(self, q1: float, q2: float) -> Tuple[float, float, float]:
        """
        Compute 3D position in the pyramid.

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Tuple of (x, y, z) coordinates where z is height
        """
        height = self.compute_height(q1, q2)

        # Map Q1 and Q2 to x, y coordinates at the given height
        x = q1 * (1.0 - height)
        y = q2 * (1.0 - height)
        z = height

        return (x, y, z)

    def distance_to_apex(self, q1: float, q2: float) -> float:
        """
        Compute Euclidean distance to apex (perfect knowledge).

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Distance to apex
        """
        return math.sqrt(q1**2 + q2**2)

    def uncertainty_decomposition(
        self,
        q1: float,
        q2: float
    ) -> dict:
        """
        Decompose total uncertainty into components.

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Dictionary with uncertainty decomposition
        """
        total_uncertainty = self.distance_to_apex(q1, q2)

        # Compute contributions based on variance decomposition
        # This ensures q1_contribution + q2_contribution = 1.0
        q1_squared = q1 ** 2
        q2_squared = q2 ** 2
        total_variance = q1_squared + q2_squared

        # Avoid division by zero
        if total_variance < 1e-6:
            q1_ratio = 0.5
            q2_ratio = 0.5
        else:
            q1_ratio = q1_squared / total_variance
            q2_ratio = q2_squared / total_variance

        return {
            "total_uncertainty": total_uncertainty,
            "q1_contribution": q1_ratio,
            "q2_contribution": q2_ratio,
            "dominant_uncertainty": "aleatoric" if q1 > q2 else "epistemic",
        }

    def epistemic_equilibrium_score(self, q1: float, q2: float) -> float:
        """
        Compute epistemic equilibrium score.

        A balanced pyramid has Q1 ≈ Q2. Imbalance suggests:
        - Q1 >> Q2: Data is noisy but model is confident
        - Q2 >> Q1: Data is clear but model is uncertain (hallucination risk)

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Equilibrium score [0, 1] where 1 = perfect balance
        """
        if q1 + q2 < 1e-6:
            return 1.0  # Both near zero is balanced

        ratio = min(q1, q2) / max(q1, q2)
        return ratio  # 1.0 = perfect balance, 0.0 = extreme imbalance


class PyramidalLaw:
    """
    The Pyramidal Law for epistemic equilibrium.

    Key principle: Total uncertainty decreases as height increases,
    with Q1 and Q2 decomposing orthogonally at each level.
    """

    @staticmethod
    def validate_uncertainties(q1: float, q2: float) -> bool:
        """
        Validate uncertainty values satisfy pyramidal constraints.

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            True if valid, False otherwise
        """
        # Both must be in [0, 1]
        if not (0 <= q1 <= 1 and 0 <= q2 <= 1):
            return False

        # Total uncertainty cannot exceed sqrt(2) (diagonal of unit square)
        total = math.sqrt(q1**2 + q2**2)
        if total > math.sqrt(2):
            return False

        return True

    @staticmethod
    def intervention_strategy(q1: float, q2: float) -> str:
        """
        Recommend intervention based on uncertainty decomposition.

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty

        Returns:
            Intervention recommendation
        """
        if q1 > 0.4 and q2 < 0.2:
            return "CLARIFY_QUESTION"  # High aleatoric - question is ambiguous

        if q2 > 0.3 and q1 < 0.2:
            return "RETRIEVE_MORE_DATA"  # High epistemic - model needs more info

        if q1 > 0.3 and q2 > 0.3:
            return "ESCALATE_TO_EXPERT"  # Both high - complex case

        if q1 < 0.2 and q2 < 0.2:
            return "TRUST_RESPONSE"  # Both low - reliable

        return "REVIEW_RECOMMENDED"  # Moderate uncertainty


# ============================================================================
# LEVEL 1: NEURAL PYRAMIDAL COMPONENTS (pyramidal_q1q2)
# ============================================================================


class HeightGate(nn.Module):
    """
    Neural Height Gate (Level 1 - pyramidal_q1q2).

    Learns to predict epistemic height (proximity to truth) as a trainable gate,
    rather than just computing it from Q1/Q2.

    Architecture:
        Input: [embeddings (384), q1 (1), q2 (1)] = 386 dims
        Hidden: [128, 64] with ReLU
        Output: height ∈ [0, 1] via Sigmoid

    Supervision:
        height* = 1 - sqrt(Q1*² + Q2*²)
        where Q1*, Q2* are ground truth uncertainties

    Benefits:
        - Provides richer signal than passive calculation
        - Can learn non-linear height patterns
        - Improves Q2 calibration via height-aware gating
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dims: Tuple[int, int] = (128, 64),
        dropout: float = 0.1
    ):
        """
        Initialize Height Gate.

        Args:
            input_dim: Embedding dimension (384 for all-MiniLM-L6-v2)
            hidden_dims: Hidden layer dimensions
            dropout: Dropout probability for regularization
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims

        # Network: [embeddings, q1, q2] → height
        # Input: input_dim + 2 (for q1 and q2)
        layers = []

        # Input layer
        current_dim = input_dim + 2
        layers.append(nn.Linear(current_dim, hidden_dims[0]))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout))

        # Hidden layers
        for i in range(len(hidden_dims) - 1):
            layers.append(nn.Linear(hidden_dims[i], hidden_dims[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))

        # Output layer
        layers.append(nn.Linear(hidden_dims[-1], 1))
        layers.append(nn.Sigmoid())  # Height ∈ [0, 1]

        self.network = nn.Sequential(*layers)

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
        q1: torch.Tensor,
        q2: torch.Tensor
    ) -> torch.Tensor:
        """
        Predict epistemic height.

        Args:
            embeddings: Text embeddings, shape (batch_size, input_dim) or (input_dim,)
            q1: Aleatoric uncertainty, shape (batch_size, 1) or (1,)
            q2: Epistemic uncertainty, shape (batch_size, 1) or (1,)

        Returns:
            Height values ∈ [0, 1], shape (batch_size, 1) or (1,)
        """
        # Handle single sample
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        # Ensure q1, q2 have correct shape
        if q1.dim() == 0 or (q1.dim() == 1 and q1.size(0) != embeddings.size(0)):
            q1 = q1.unsqueeze(0) if q1.dim() == 0 else q1
            if q1.dim() == 1:
                q1 = q1.unsqueeze(1)

        if q2.dim() == 0 or (q2.dim() == 1 and q2.size(0) != embeddings.size(0)):
            q2 = q2.unsqueeze(0) if q2.dim() == 0 else q2
            if q2.dim() == 1:
                q2 = q2.unsqueeze(1)

        # Concatenate inputs: [embeddings, q1, q2]
        x = torch.cat([embeddings, q1, q2], dim=-1)

        # Forward pass
        height = self.network(x)

        # Remove batch dimension for single sample
        if single_sample:
            height = height.squeeze(0)

        return height


class BaseForcesNetwork(nn.Module):
    """
    Base Forces Network (Level 1 - pyramidal_q1q2).

    Implements the 4-force pyramidal base from "How to Solve Skynet":
        1. Memory: Past experience and learned patterns
        2. Pain: Error signals and correction pressure
        3. Choice: Decision-making under uncertainty
        4. Exploration: Curiosity and knowledge-seeking

    Architecture:
        Input: embeddings (384)
        Hidden: [128] with ReLU
        Output: 4 forces via Softmax (sum to 1.0)

    Base Stability:
        stability = 1 - variance(forces)
        Ideal: all forces = 0.25 (perfect balance)
        Poor: one force >> others (imbalanced, risk of collapse)

    Benefits:
        - Prevents Q1 gate collapse (overconfidence)
        - Provides equilibrium signal for calibration
        - Interpretable force decomposition
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 128,
        dropout: float = 0.1
    ):
        """
        Initialize Base Forces Network.

        Args:
            input_dim: Embedding dimension
            hidden_dim: Hidden layer dimension
            dropout: Dropout probability
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Network: embeddings → 4 forces
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 4),  # 4 forces
            nn.Softmax(dim=-1)  # Forces sum to 1.0
        )

        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Predict 4-force weights.

        Args:
            embeddings: Text embeddings, shape (batch_size, input_dim) or (input_dim,)

        Returns:
            Force weights [memory, pain, choice, exploration],
            shape (batch_size, 4) or (4,)
        """
        # Handle single sample
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        # Forward pass
        forces = self.network(embeddings)

        # Remove batch dimension for single sample
        if single_sample:
            forces = forces.squeeze(0)

        return forces

    def compute_stability(self, forces: torch.Tensor) -> torch.Tensor:
        """
        Compute base stability from force weights.

        Base stability = 1 - variance(forces)

        Perfect balance: forces = [0.25, 0.25, 0.25, 0.25] → stability = 1.0
        Imbalanced: forces = [0.7, 0.1, 0.1, 0.1] → stability < 1.0

        Args:
            forces: Force weights, shape (batch_size, 4) or (4,)

        Returns:
            Stability values ∈ [0, 1], shape (batch_size,) or scalar
        """
        # Variance across the 4 forces
        variance = torch.var(forces, dim=-1)
        stability = 1.0 - variance

        # Clamp to [0, 1] (variance could theoretically exceed 1)
        stability = torch.clamp(stability, 0.0, 1.0)

        return stability

    def decompose_forces(self, forces: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Decompose force weights into named components.

        Args:
            forces: Force weights, shape (batch_size, 4) or (4,)

        Returns:
            Dictionary with force names and values
        """
        if forces.dim() == 1:
            return {
                "memory": forces[0],
                "pain": forces[1],
                "choice": forces[2],
                "exploration": forces[3]
            }
        else:
            return {
                "memory": forces[:, 0],
                "pain": forces[:, 1],
                "choice": forces[:, 2],
                "exploration": forces[:, 3]
            }


class PyramidalLevel1:
    """
    Complete Level 1 Pyramidal Architecture (pyramidal_q1q2).

    Combines:
        - Q1/Q2 gates (aleatoric + epistemic uncertainty)
        - Height gate (neural, trainable)
        - Base forces (4-force equilibrium)
        - Temperature modulation (height-aware)

    This is a wrapper/coordinator class. Actual training happens in train.py
    using the individual neural components (HeightGate, BaseForcesNetwork).

    Note: This is equivalent to pyramidal_q1q2 in aletheion-llm.
    """

    def __init__(
        self,
        height_gate: HeightGate,
        base_forces: BaseForcesNetwork,
        base_temperature: float = 1.0
    ):
        """
        Initialize Level 2 architecture.

        Args:
            height_gate: Trained HeightGate instance
            base_forces: Trained BaseForcesNetwork instance
            base_temperature: Base temperature tau_0 for modulation
        """
        self.height_gate = height_gate
        self.base_forces = base_forces
        self.tau_0 = base_temperature

    def compute_temperature(self, height: torch.Tensor) -> torch.Tensor:
        """
        Compute adaptive temperature based on epistemic height.

        Temperature modulation:
            tau = tau_0 / (1 + height)

        Low height (high uncertainty) → high temperature → flatter distribution
        High height (low uncertainty) → low temperature → sharper distribution

        Args:
            height: Epistemic height ∈ [0, 1]

        Returns:
            Temperature values
        """
        temperature = self.tau_0 / (1.0 + height + 1e-8)  # epsilon for stability
        return temperature

    def validate_pyramidal_constraints(
        self,
        q1: torch.Tensor,
        q2: torch.Tensor,
        height: torch.Tensor,
        base_stability: torch.Tensor
    ) -> Dict[str, bool]:
        """
        Validate that pyramidal constraints are satisfied.

        Constraints:
            1. Q1, Q2 ∈ [0, 1]
            2. height ∈ [0, 1]
            3. base_stability ∈ [0, 1]
            4. height ≈ 1 - sqrt(q1² + q2²) (within tolerance)
            5. base_stability > 0.5 (reasonable balance)

        Args:
            q1: Aleatoric uncertainty
            q2: Epistemic uncertainty
            height: Epistemic height
            base_stability: Base stability

        Returns:
            Dictionary of validation results
        """
        tolerance = 0.1

        # Compute geometric height
        height_geometric = 1.0 - torch.sqrt(q1**2 + q2**2)
        height_diff = torch.abs(height - height_geometric).mean()

        return {
            "q1_in_range": bool((q1 >= 0).all() and (q1 <= 1).all()),
            "q2_in_range": bool((q2 >= 0).all() and (q2 <= 1).all()),
            "height_in_range": bool((height >= 0).all() and (height <= 1).all()),
            "stability_in_range": bool((base_stability >= 0).all() and (base_stability <= 1).all()),
            "height_consistent": bool(height_diff < tolerance),
            "stability_adequate": bool((base_stability > 0.5).all()),
            "all_valid": bool(
                (q1 >= 0).all() and (q1 <= 1).all() and
                (q2 >= 0).all() and (q2 <= 1).all() and
                (height >= 0).all() and (height <= 1).all() and
                (base_stability >= 0).all() and (base_stability <= 1).all() and
                height_diff < tolerance and
                (base_stability > 0.5).all()
            )
        }


# ============================================================================
# BACKWARDS COMPATIBILITY ALIAS
# ============================================================================

# For backwards compatibility with existing code
PyramidalLevel2 = PyramidalLevel1


# ============================================================================
# LEVEL 2: ATTENTION HEAD MECHANISM (planned)
# ============================================================================

class AttentionHead(nn.Module):
    """
    Attention Head for Level 2 (planned implementation).

    Adds attention mechanism to Level 1 pyramidal_q1q2 architecture
    to improve uncertainty calibration through selective focus on
    different parts of the input.

    TODO: Implement attention head mechanism as described in aletheion-llm Level 2
    """

    def __init__(self):
        super().__init__()
        raise NotImplementedError(
            "Level 2 (Attention Head) is not yet implemented. "
            "Currently only Level 1 (pyramidal_q1q2) is available."
        )


# ============================================================================
# LEVEL 3: FULL FRACTAL (planned)
# ============================================================================

class FractalUncertainty(nn.Module):
    """
    Fractal meta-epistemic uncertainty for Level 3 (planned implementation).

    Implements "uncertainty about uncertainty" - measuring how certain
    we are about our uncertainty estimates themselves.

    TODO: Implement full fractal architecture as described in aletheion-llm Level 3
    """

    def __init__(self):
        super().__init__()
        raise NotImplementedError(
            "Level 3 (Full Fractal) is not yet implemented. "
            "Currently only Level 1 (pyramidal_q1q2) is available."
        )
