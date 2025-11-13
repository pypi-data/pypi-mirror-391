# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Configuration management for AletheionGuard API.

Handles environment variables and settings for both Managed and BYO-HF modes.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        HF_ENDPOINT_URL: Default Hugging Face endpoint/Space URL for Managed mode
        HF_SPACE_URL: Alias for HF_ENDPOINT_URL (for clarity when using HF Spaces)
        HF_TOKEN: Default Hugging Face token for Managed mode
        AG_API_KEY_SECRET: Secret for API key validation (JWT/HMAC)
        ALLOWED_HF_HOSTS: Comma-separated list of allowed HF hosts for BYO-HF
        HF_TIMEOUT: Timeout in seconds for HF requests (max 60s for security)
        MAX_TIMEOUT: Maximum allowed timeout (SEC-009)
        CORS_ORIGINS: Comma-separated list of allowed CORS origins (SEC-008)
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    # Managed mode settings
    HF_ENDPOINT_URL: Optional[str] = None
    HF_SPACE_URL: Optional[str] = None  # Alias for HF_ENDPOINT_URL
    HF_TOKEN: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If HF_SPACE_URL is set but HF_ENDPOINT_URL is not, use HF_SPACE_URL
        if self.HF_SPACE_URL and not self.HF_ENDPOINT_URL:
            self.HF_ENDPOINT_URL = self.HF_SPACE_URL

    # API authentication (SEC-002)
    AG_API_KEY_SECRET: Optional[str] = None

    # BYO-HF security settings
    ALLOWED_HF_HOSTS: str = "huggingface.co,hf.space,endpoints.huggingface.cloud"

    # Performance settings
    HF_TIMEOUT: float = 30.0
    MAX_TIMEOUT: float = 60.0  # SEC-009: Maximum allowed timeout

    # CORS settings (SEC-008)
    CORS_ORIGINS: str = "*"  # Default allows all, should be configured in production

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator('HF_TIMEOUT')
    @classmethod
    def validate_timeout(cls, v, info):
        """Validate that timeout doesn't exceed maximum (SEC-009)."""
        max_timeout = info.data.get('MAX_TIMEOUT', 60.0)
        if v > max_timeout:
            return max_timeout
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
