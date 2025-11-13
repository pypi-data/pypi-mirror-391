# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Input processor for text embeddings using sentence-transformers.

This module handles text encoding for the AletheionGuard epistemic auditor.
"""

from typing import Union, List, Optional
import torch
import numpy as np
from sentence_transformers import SentenceTransformer


class InputProcessor:
    """
    Process text inputs into embeddings for uncertainty estimation.

    Uses sentence-transformers/all-MiniLM-L6-v2 model which produces
    384-dimensional embeddings.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        """
        Initialize the input processor.

        Args:
            model_name: Name of the sentence-transformers model
            device: Device to run on ('cpu', 'cuda', 'mps', 'auto', or None for auto-detection)
        """
        self.model_name = model_name

        # Auto-detect device if not specified or if 'auto' is passed
        if device is None or device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.device = device

        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Verify we have the expected dimension (384 for all-MiniLM-L6-v2)
        assert self.embedding_dim == 384, f"Expected 384-dim embeddings, got {self.embedding_dim}"

    def encode(
        self,
        text: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> torch.Tensor:
        """
        Encode text into embeddings.

        Args:
            text: Single text string or list of strings
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            normalize: L2-normalize embeddings

        Returns:
            Tensor of shape (n_texts, 384) or (384,) for single input
        """
        # Convert single string to list
        is_single = isinstance(text, str)
        if is_single:
            text = [text]

        # Encode using sentence-transformers
        embeddings = self.model.encode(
            text,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_tensor=True,
            normalize_embeddings=normalize,
            device=self.device
        )

        # Return single embedding if input was single string
        if is_single:
            return embeddings[0]

        return embeddings

    def encode_with_context(
        self,
        text: Union[str, List[str]],
        context: Optional[Union[str, List[str]]] = None,
        separator: str = " [SEP] "
    ) -> torch.Tensor:
        """
        Encode text with optional context.

        Context is prepended to the text with a separator.

        Args:
            text: Main text to encode
            context: Optional context to prepend
            separator: Separator between context and text

        Returns:
            Embeddings tensor
        """
        # Handle context
        if context is not None:
            if isinstance(text, str):
                # Single text + context
                combined = f"{context}{separator}{text}"
            else:
                # Multiple texts + contexts
                if isinstance(context, str):
                    # Same context for all texts
                    combined = [f"{context}{separator}{t}" for t in text]
                else:
                    # Different context for each text
                    assert len(context) == len(text), "Context and text lists must match"
                    combined = [f"{c}{separator}{t}" for c, t in zip(context, text)]

            return self.encode(combined)

        return self.encode(text)

    def get_embedding_dim(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dim

    def to(self, device: str):
        """Move model to specified device."""
        self.device = device
        self.model = self.model.to(device)
        return self

    def __repr__(self) -> str:
        return f"InputProcessor(model={self.model_name}, device={self.device}, dim={self.embedding_dim})"


def create_input_processor(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: Optional[str] = None
) -> InputProcessor:
    """
    Factory function to create an InputProcessor.

    Args:
        model_name: Name of the sentence-transformers model
        device: Device to run on

    Returns:
        InputProcessor instance
    """
    return InputProcessor(model_name=model_name, device=device)
