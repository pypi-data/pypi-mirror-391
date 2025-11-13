# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Q1 and Q2 gates for aleatoric and epistemic uncertainty estimation.

This module implements neural networks for estimating:
- Q1 (aleatoric uncertainty): Irreducible data noise and ambiguity
- Q2 (epistemic uncertainty): Model ignorance and hallucination risk

Mathematical formulation from "How to Solve Skynet v1.1":
- Q1* = 1 - p(y* | x)  [probability of correct token]
- Q2* = 1/2 * [(1 - 1[argmax p = y*]) + H(p)/log V]  [correctness + entropy]
- Height: h = 1 - sqrt(Q1² + Q2²)
"""

from typing import Optional, Union
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class UncertaintyNetwork(nn.Module):
    """
    Base neural network for uncertainty estimation.

    Architecture (MLP):
    - Input: Text embeddings (384-dim from sentence transformers)
    - Hidden layers: [256, 256] with ReLU activation
    - Output: Single uncertainty value [0, 1] with Sigmoid

    Mathematical formulation:
        h1 = ReLU(W1 * x + b1)
        h2 = ReLU(W2 * h1 + b2)
        h3 = ReLU(W3 * h2 + b3)
        output = Sigmoid(h3)
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 256,
        num_layers: int = 3,
        dropout: float = 0.1
    ):
        """
        Initialize uncertainty network.

        Args:
            input_dim: Input embedding dimension (384 for all-MiniLM-L6-v2)
            hidden_dim: Hidden layer dimension
            num_layers: Number of hidden layers
            dropout: Dropout probability for regularization
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Build MLP layers
        layers = []

        # Input layer
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout))

        # Hidden layers
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))

        # Output layer (single uncertainty value)
        layers.append(nn.Linear(hidden_dim, 1))
        layers.append(nn.Sigmoid())  # Clamp to [0, 1]

        self.network = nn.Sequential(*layers)

        # Initialize weights with Xavier initialization
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights using Xavier uniform initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            x: Input tensor of shape (batch_size, input_dim) or (input_dim,)

        Returns:
            Uncertainty values of shape (batch_size, 1) or (1,)
        """
        # Handle single sample (add batch dimension)
        if x.dim() == 1:
            x = x.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        output = self.network(x)

        # Remove batch dimension for single sample
        if single_sample:
            output = output.squeeze(0)

        return output


class Q1Gate(nn.Module):
    """
    Aleatoric uncertainty gate (Q1).

    Estimates irreducible uncertainty from data noise and ambiguity.

    Supervised by: Q1* = 1 - p(y* | x)
    where p(y* | x) is the probability of the correct token.
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 256,
        config: Optional[dict] = None
    ):
        """
        Initialize Q1 gate.

        Args:
            input_dim: Input embedding dimension
            hidden_dim: Hidden layer dimension
            config: Optional configuration dictionary
        """
        super().__init__()

        self.config = config or {}
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Create the uncertainty network
        self.network = UncertaintyNetwork(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=3,
            dropout=self.config.get("dropout", 0.1)
        )

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Estimate aleatoric uncertainty.

        Args:
            embeddings: Text embeddings of shape (batch_size, input_dim) or (input_dim,)

        Returns:
            Q1 values in [0, 1] of shape (batch_size, 1) or (1,)
        """
        return self.network(embeddings)


class Q2Gate(nn.Module):
    """
    Epistemic uncertainty gate (Q2).

    Estimates model ignorance and hallucination risk.
    Conditioned on Q1 for better calibration.

    Supervised by: Q2* = 1/2 * [(1 - 1[argmax p = y*]) + H(p)/log V]
    where H(p) is entropy and V is vocabulary size.
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 256,
        config: Optional[dict] = None
    ):
        """
        Initialize Q2 gate.

        Args:
            input_dim: Input embedding dimension
            hidden_dim: Hidden layer dimension
            config: Optional configuration dictionary
        """
        super().__init__()

        self.config = config or {}
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Q2 is conditioned on Q1, so input is embeddings + Q1 value
        # Input: [embeddings (384), q1 (1)] = 385 dimensions
        self.network = UncertaintyNetwork(
            input_dim=input_dim + 1,  # +1 for Q1 conditioning
            hidden_dim=hidden_dim,
            num_layers=3,
            dropout=self.config.get("dropout", 0.1)
        )

    def forward(
        self,
        embeddings: torch.Tensor,
        q1: Union[torch.Tensor, float]
    ) -> torch.Tensor:
        """
        Estimate epistemic uncertainty.

        Args:
            embeddings: Text embeddings of shape (batch_size, input_dim) or (input_dim,)
            q1: Aleatoric uncertainty (conditioning variable), scalar or tensor

        Returns:
            Q2 values in [0, 1]
        """
        # Handle single sample
        if embeddings.dim() == 1:
            embeddings = embeddings.unsqueeze(0)
            single_sample = True
        else:
            single_sample = False

        # Convert Q1 to tensor if needed
        if isinstance(q1, float):
            q1 = torch.tensor([[q1]], dtype=embeddings.dtype, device=embeddings.device)
        elif q1.dim() == 0:
            q1 = q1.unsqueeze(0).unsqueeze(0)
        elif q1.dim() == 1:
            q1 = q1.unsqueeze(1)

        # Concatenate embeddings with Q1 for conditioning
        # Shape: (batch_size, input_dim + 1)
        combined = torch.cat([embeddings, q1], dim=1)

        output = self.network(combined)

        # Remove batch dimension for single sample
        if single_sample:
            output = output.squeeze(0)

        return output


def create_q1_gate(
    input_dim: int = 384,
    hidden_dim: int = 256,
    weights_path: Optional[str] = None
) -> Q1Gate:
    """
    Factory function to create a Q1 gate.

    Args:
        input_dim: Input embedding dimension
        hidden_dim: Hidden layer dimension
        weights_path: Path to pretrained weights (optional)

    Returns:
        Q1Gate instance
    """
    gate = Q1Gate(input_dim=input_dim, hidden_dim=hidden_dim)

    if weights_path is not None:
        gate.load_state_dict(torch.load(weights_path))

    return gate


def create_q2_gate(
    input_dim: int = 384,
    hidden_dim: int = 256,
    weights_path: Optional[str] = None
) -> Q2Gate:
    """
    Factory function to create a Q2 gate.

    Args:
        input_dim: Input embedding dimension
        hidden_dim: Hidden layer dimension
        weights_path: Path to pretrained weights (optional)

    Returns:
        Q2Gate instance
    """
    gate = Q2Gate(input_dim=input_dim, hidden_dim=hidden_dim)

    if weights_path is not None:
        gate.load_state_dict(torch.load(weights_path))

    return gate
