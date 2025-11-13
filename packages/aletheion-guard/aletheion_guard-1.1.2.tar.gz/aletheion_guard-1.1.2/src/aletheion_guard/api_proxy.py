# PROPRIETARY AND CONFIDENTIAL
# Copyright (c) 2024-2025 AletheionAGI
# Unauthorized copying prohibited
#
# LEVEL 3 SECURITY COMPONENT
# This file contains proprietary API proxy implementations
# that are confidential and not covered by AGPL-3.0

"""
Hugging Face API proxy client for both Managed and BYO-HF modes.

Handles upstream communication with HF endpoints, supporting both default
(Managed) and client-provided (BYO-HF) configurations.
"""

import httpx
from typing import Optional
import logging

from .security import mask_token

logger = logging.getLogger(__name__)


class HFClient:
    """
    HTTP client for Hugging Face inference endpoints.

    Supports both Managed mode (default endpoint/token from env) and
    BYO-HF mode (client-provided endpoint/token via headers).

    Attributes:
        default_url: Default HF endpoint URL (Managed mode)
        default_token: Default HF token (Managed mode)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        default_url: Optional[str] = None,
        default_token: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize HF client.

        Args:
            default_url: Default Hugging Face endpoint URL
            default_token: Default Hugging Face API token
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.default_url = default_url.rstrip("/") if default_url else None
        self.default_token = default_token
        self.timeout = timeout

        logger.info(
            f"HFClient initialized - "
            f"default_url={'configured' if default_url else 'None'}, "
            f"default_token={mask_token(default_token)}"
        )

    async def predict(
        self,
        text: str,
        context: Optional[str] = None,
        hf_url: Optional[str] = None,
        hf_token: Optional[str] = None
    ) -> httpx.Response:
        """
        Call HF /predict endpoint.

        Uses BYO-HF parameters if provided, otherwise falls back to defaults.

        Args:
            text: Text to analyze
            context: Optional context for the text
            hf_url: Optional BYO-HF endpoint URL (overrides default)
            hf_token: Optional BYO-HF token (overrides default)

        Returns:
            httpx.Response object with prediction results

        Raises:
            ValueError: If no endpoint/token configured (neither default nor BYO-HF)
            httpx.HTTPError: If upstream request fails

        Example:
            >>> client = HFClient(default_url="https://...", default_token="hf_...")
            >>> # Managed mode
            >>> response = await client.predict("Some text", "context")
            >>> # BYO-HF mode
            >>> response = await client.predict(
            ...     "Some text",
            ...     "context",
            ...     hf_url="https://custom.hf.space",
            ...     hf_token="hf_custom123"
            ... )
        """
        # Determine URL and token (BYO-HF overrides default)
        url = hf_url or self.default_url
        token = hf_token or self.default_token

        # Validate configuration
        if not url or not token:
            raise ValueError(
                "HF upstream missing configuration. "
                "Either provide X-HF-Endpoint/X-HF-Token headers (BYO-HF) "
                "or set HF_ENDPOINT_URL/HF_TOKEN environment variables (Managed)."
            )

        mode = "byo-hf" if (hf_url or hf_token) else "managed"
        logger.info(
            f"Calling HF predict - mode={mode}, "
            f"url={url}, token={mask_token(token)}"
        )

        # Build request
        payload = {"text": text}
        if context is not None:
            payload["context"] = context

        headers = {"Authorization": f"Bearer {token}"}

        # Make request (SEC-005: prevent SSRF via redirects)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{url.rstrip('/')}/predict",
                    json=payload,
                    headers=headers,
                    follow_redirects=False  # SEC-005: Prevent SSRF via HTTP redirects
                )
                response.raise_for_status()

                logger.info(
                    f"HF predict success - mode={mode}, "
                    f"status={response.status_code}, "
                    f"latency={response.elapsed.total_seconds() * 1000:.1f}ms"
                )

                return response

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HF predict failed - mode={mode}, "
                    f"status={e.response.status_code}, "
                    f"error={str(e)}"
                )
                raise

            except httpx.RequestError as e:
                logger.error(
                    f"HF predict request error - mode={mode}, "
                    f"error={str(e)}"
                )
                raise
