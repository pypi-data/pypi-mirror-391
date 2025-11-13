# http_utils.py
"""Shared HTTP utilities for Rebrandly OTEL SDK."""

import os
import json
from typing import Any, Dict, Optional


# ============================================
# CONSTANTS
# ============================================

# Sensitive field names to redact from request bodies (case-insensitive matching)
SENSITIVE_FIELD_NAMES = [
    'password',
    'passwd',
    'pwd',
    'token',
    'access_token',
    'accesstoken',
    'refresh_token',
    'refreshtoken',
    'auth_token',
    'authtoken',
    'apikey',
    'api_key',
    'api-key',
    'secret',
    'client_secret',
    'clientsecret',
    'authorization',
    'creditcard',
    'credit_card',
    'cardnumber',
    'card_number',
    'cvv',
    'cvc',
    'ssn',
    'social_security',
    'socialsecurity'
]

# Content types that should be captured (JSON only)
CAPTURABLE_CONTENT_TYPES = [
    'application/json',
    'application/ld+json',
    'application/vnd.api+json'
]


# ============================================
# HEADER FILTERING
# ============================================

def filter_important_headers(headers):
    """
    Filter headers to keep only important ones for observability.
    Excludes sensitive headers like authorization, cookies, and tokens.
    """
    important_headers = [
        'content-type',
        'content-length',
        'accept',
        'accept-encoding',
        'accept-language',
        'host',
        'x-forwarded-for',
        'x-forwarded-proto',
        'x-request-id',
        'x-correlation-id',
        'x-trace-id',
        'user-agent'
    ]

    filtered = {}
    for key, value in headers.items():
        if key.lower() in important_headers:
            filtered[key] = value
    return filtered


# ============================================
# REQUEST BODY CAPTURE
# ============================================

def is_body_capture_enabled() -> bool:
    """
    Check if request body capture is enabled.
    Enabled by default (opt-out model), can be disabled via environment variable.

    Returns:
        bool: True if body capture is enabled

    Example:
        # Disable body capture
        os.environ['OTEL_CAPTURE_REQUEST_BODY'] = 'false'
        is_body_capture_enabled()  # Returns: False
    """
    env_value = os.environ.get('OTEL_CAPTURE_REQUEST_BODY', '').lower()
    if not env_value:
        return True  # Enabled by default
    return env_value not in ('false', '0', 'no')


def should_capture_body(content_type: Optional[str]) -> bool:
    """
    Check if content type should be captured.
    Only JSON content types are captured (application/json and variants).

    Args:
        content_type: Content-Type header value

    Returns:
        bool: True if content type should be captured

    Example:
        should_capture_body('application/json')  # Returns: True
        should_capture_body('application/json; charset=utf-8')  # Returns: True
        should_capture_body('text/html')  # Returns: False
        should_capture_body('multipart/form-data')  # Returns: False
    """
    if not content_type or not isinstance(content_type, str):
        return False

    # Extract base content type (before semicolon for charset, etc.)
    base_content_type = content_type.split(';')[0].strip().lower()

    # Check if it matches any capturable content type
    return any(
        base_content_type == ct or base_content_type.endswith('+json')
        for ct in CAPTURABLE_CONTENT_TYPES
    )


def redact_sensitive_fields(obj: Any) -> Any:
    """
    Recursively redact sensitive fields from an object.
    Creates a deep copy to avoid mutating the original object.

    Args:
        obj: Object to redact (can be dict, list, or primitive)

    Returns:
        Any: Redacted copy of the object

    Example:
        data = {'username': 'john', 'password': 'secret123', 'nested': {'token': 'abc'}}
        redact_sensitive_fields(data)
        # Returns: {'username': 'john', 'password': '[REDACTED]', 'nested': {'token': '[REDACTED]'}}
    """
    # Handle None and primitives
    if obj is None or not isinstance(obj, (dict, list)):
        return obj

    # Handle lists
    if isinstance(obj, list):
        return [redact_sensitive_fields(item) for item in obj]

    # Handle dictionaries
    redacted = {}
    for key, value in obj.items():
        lower_key = key.lower() if isinstance(key, str) else str(key).lower()

        # Check if key matches any sensitive field name
        # Only match if the key exactly matches or contains the sensitive name
        # (not if the sensitive name contains the key, to avoid false positives like "auth" matching "auth_token")
        is_sensitive = any(
            lower_key == sensitive_name or
            sensitive_name in lower_key
            for sensitive_name in SENSITIVE_FIELD_NAMES
        )

        if is_sensitive:
            redacted[key] = '[REDACTED]'
        elif isinstance(value, (dict, list)):
            # Recursively redact nested objects and arrays
            redacted[key] = redact_sensitive_fields(value)
        else:
            redacted[key] = value

    return redacted


def capture_request_body(body: Any, content_type: Optional[str]) -> Optional[str]:
    """
    Capture and process request body for telemetry.
    Handles JSON parsing, content-type filtering, and sensitive data redaction.

    Args:
        body: Request body (can be string, dict, bytes, or other)
        content_type: Content-Type header value

    Returns:
        Optional[str]: Processed body as JSON string, or None if not capturable

    Example:
        # With parsed dict body
        body = {'user': 'john', 'password': 'secret'}
        capture_request_body(body, 'application/json')
        # Returns: '{"user":"john","password":"[REDACTED]"}'

        # With string body
        body = '{"user":"john","password":"secret"}'
        capture_request_body(body, 'application/json')
        # Returns: '{"user":"john","password":"[REDACTED]"}'

        # With non-JSON content type
        capture_request_body(body, 'text/html')
        # Returns: None
    """
    try:
        # Check if body capture is enabled
        if not is_body_capture_enabled():
            return None

        # Check if content type should be captured
        if not should_capture_body(content_type):
            return None

        # Handle empty body
        if not body:
            return None

        # Parse body if it's a string or bytes
        parsed_body = body
        if isinstance(body, str):
            try:
                parsed_body = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                # If parsing fails, return None (invalid JSON)
                return None
        elif isinstance(body, bytes):
            try:
                parsed_body = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                return None

        # Redact sensitive fields
        redacted = redact_sensitive_fields(parsed_body)

        # Convert back to JSON string
        return json.dumps(redacted)
    except Exception as e:
        # Silently fail - don't break the request if body capture fails
        print(f'[Rebrandly OTEL] Body capture failed: {str(e)}')
        return None
