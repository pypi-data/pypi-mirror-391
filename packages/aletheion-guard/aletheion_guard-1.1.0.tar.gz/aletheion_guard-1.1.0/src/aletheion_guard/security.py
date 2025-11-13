# PROPRIETARY AND CONFIDENTIAL
# Copyright (c) 2024-2025 AletheionAGI
# Unauthorized copying prohibited
#
# LEVEL 3 SECURITY COMPONENT
# This file contains proprietary security implementations
# that are confidential and not covered by AGPL-3.0

"""
Security utilities for BYO-HF mode.

Provides endpoint validation and token masking to prevent security issues.
"""

import re
import ipaddress
import secrets
from urllib.parse import urlparse
from typing import Optional
from .config import settings


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key using constant-time comparison (SEC-002).

    Args:
        api_key: The API key to verify

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not settings.AG_API_KEY_SECRET:
        return False

    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(api_key, settings.AG_API_KEY_SECRET)


def mask_token(token: Optional[str]) -> str:
    """
    Mask a token for safe logging.

    Shows only the first 7 characters (e.g., "hf_xxxx") and masks the rest.

    Args:
        token: The token to mask (e.g., "hf_abcd1234567890")

    Returns:
        Masked token (e.g., "hf_abcd***")

    Example:
        >>> mask_token("hf_abcd1234567890")
        'hf_abcd***'
        >>> mask_token(None)
        'None'
    """
    if not token:
        return "None"

    if len(token) <= 10:
        # Too short, mask everything after prefix
        return token[:3] + "***"

    # Show first 7 chars, mask the rest
    return token[:7] + "***"


def validate_endpoint(endpoint: str) -> bool:
    """
    Validate a Hugging Face endpoint URL for security.

    Security checks:
    1. Must use HTTPS (not HTTP)
    2. Must not be localhost or private IP
    3. Host must be in ALLOWED_HF_HOSTS allowlist

    Args:
        endpoint: The endpoint URL to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_endpoint("https://api-inference.huggingface.co/predict")
        True
        >>> validate_endpoint("http://localhost:8000/predict")
        False
        >>> validate_endpoint("https://192.168.1.1/predict")
        False
    """
    if not endpoint:
        return False

    try:
        parsed = urlparse(endpoint)

        # Check 1: Must use HTTPS
        if parsed.scheme != "https":
            return False

        # Check 2: Block localhost
        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
            return False

        # Check 3: Block private IPs (basic check)
        if _is_private_ip(hostname):
            return False

        # Check 4: Validate against allowlist
        allowed_hosts = [h.strip() for h in settings.ALLOWED_HF_HOSTS.split(",")]

        # Check if hostname matches or is a subdomain of allowed hosts
        hostname_valid = any(
            hostname == allowed or hostname.endswith(f".{allowed}")
            for allowed in allowed_hosts
        )

        return hostname_valid

    except Exception:
        return False


def _is_private_ip(hostname: str) -> bool:
    """
    Check if hostname is a private IP address (SEC-006).

    Uses Python's ipaddress module for robust IPv4 and IPv6 validation.

    Args:
        hostname: The hostname to check

    Returns:
        True if private IP, False otherwise
    """
    try:
        # Try to parse as IP address (supports both IPv4 and IPv6)
        ip = ipaddress.ip_address(hostname)

        # Check if IP is private, loopback, link-local, or reserved
        return (
            ip.is_private or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_reserved or
            ip.is_multicast
        )

    except ValueError:
        # Not a valid IP address, return False
        return False
