"""Tests for HTTP utilities (Body Capture)"""

import os
import pytest
from src.http_utils import (
    is_body_capture_enabled,
    should_capture_body,
    redact_sensitive_fields,
    capture_request_body
)


class TestIsBodyCaptureEnabled:
    """Tests for is_body_capture_enabled function"""

    def test_default_enabled(self, monkeypatch):
        """Should return True by default (opt-out)"""
        monkeypatch.delenv('OTEL_CAPTURE_REQUEST_BODY', raising=False)
        assert is_body_capture_enabled() is True

    def test_explicitly_disabled(self, monkeypatch):
        """Should return False when explicitly disabled"""
        monkeypatch.setenv('OTEL_CAPTURE_REQUEST_BODY', 'false')
        assert is_body_capture_enabled() is False

    def test_disabled_with_zero(self, monkeypatch):
        """Should return False when set to 0"""
        monkeypatch.setenv('OTEL_CAPTURE_REQUEST_BODY', '0')
        assert is_body_capture_enabled() is False

    def test_disabled_with_no(self, monkeypatch):
        """Should return False when set to 'no'"""
        monkeypatch.setenv('OTEL_CAPTURE_REQUEST_BODY', 'no')
        assert is_body_capture_enabled() is False

    def test_explicitly_enabled(self, monkeypatch):
        """Should return True when set to true"""
        monkeypatch.setenv('OTEL_CAPTURE_REQUEST_BODY', 'true')
        assert is_body_capture_enabled() is True


class TestShouldCaptureBody:
    """Tests for should_capture_body function"""

    def test_application_json(self):
        """Should return True for application/json"""
        assert should_capture_body('application/json') is True

    def test_application_json_with_charset(self):
        """Should return True for application/json with charset"""
        assert should_capture_body('application/json; charset=utf-8') is True

    def test_application_ld_json(self):
        """Should return True for application/ld+json"""
        assert should_capture_body('application/ld+json') is True

    def test_custom_json_type(self):
        """Should return True for custom JSON types"""
        assert should_capture_body('application/vnd.api+json') is True

    def test_text_html(self):
        """Should return False for text/html"""
        assert should_capture_body('text/html') is False

    def test_multipart_form_data(self):
        """Should return False for multipart/form-data"""
        assert should_capture_body('multipart/form-data') is False

    def test_application_octet_stream(self):
        """Should return False for application/octet-stream"""
        assert should_capture_body('application/octet-stream') is False

    def test_null_or_empty(self):
        """Should return False for null or empty"""
        assert should_capture_body(None) is False
        assert should_capture_body('') is False


class TestRedactSensitiveFields:
    """Tests for redact_sensitive_fields function"""

    def test_redact_password(self):
        """Should redact password field"""
        input_data = {'username': 'john', 'password': 'secret123'}
        result = redact_sensitive_fields(input_data)
        assert result['username'] == 'john'
        assert result['password'] == '[REDACTED]'

    def test_redact_token(self):
        """Should redact token field"""
        input_data = {'data': 'test', 'token': 'abc123'}
        result = redact_sensitive_fields(input_data)
        assert result['data'] == 'test'
        assert result['token'] == '[REDACTED]'

    def test_redact_nested_fields(self):
        """Should redact nested sensitive fields"""
        input_data = {
            'user': 'john',
            'auth': {
                'password': 'secret',
                'token': 'abc'
            }
        }
        result = redact_sensitive_fields(input_data)
        assert result['user'] == 'john'
        assert result['auth']['password'] == '[REDACTED]'
        assert result['auth']['token'] == '[REDACTED]'

    def test_redact_arrays(self):
        """Should redact fields in arrays"""
        input_data = {
            'users': [
                {'name': 'john', 'password': 'secret1'},
                {'name': 'jane', 'password': 'secret2'}
            ]
        }
        result = redact_sensitive_fields(input_data)
        assert result['users'][0]['name'] == 'john'
        assert result['users'][0]['password'] == '[REDACTED]'
        assert result['users'][1]['name'] == 'jane'
        assert result['users'][1]['password'] == '[REDACTED]'

    def test_case_insensitive(self):
        """Should handle case-insensitive matching"""
        input_data = {'PASSWORD': 'secret', 'Token': 'abc', 'ApiKey': 'xyz'}
        result = redact_sensitive_fields(input_data)
        assert result['PASSWORD'] == '[REDACTED]'
        assert result['Token'] == '[REDACTED]'
        assert result['ApiKey'] == '[REDACTED]'

    def test_no_mutation(self):
        """Should not mutate original object"""
        input_data = {'username': 'john', 'password': 'secret'}
        result = redact_sensitive_fields(input_data)
        assert input_data['password'] == 'secret'  # Original unchanged
        assert result['password'] == '[REDACTED]'

    def test_primitives(self):
        """Should handle primitives"""
        assert redact_sensitive_fields(None) is None
        assert redact_sensitive_fields('string') == 'string'
        assert redact_sensitive_fields(123) == 123


class TestCaptureRequestBody:
    """Tests for capture_request_body function"""

    def test_capture_json_dict(self):
        """Should capture and redact JSON dict body"""
        body = {'username': 'john', 'password': 'secret123'}
        result = capture_request_body(body, 'application/json')
        assert result is not None
        import json
        parsed = json.loads(result)
        assert parsed['username'] == 'john'
        assert parsed['password'] == '[REDACTED]'

    def test_capture_json_string(self):
        """Should capture and redact JSON string body"""
        body = '{"username":"john","password":"secret123"}'
        result = capture_request_body(body, 'application/json')
        assert result is not None
        import json
        parsed = json.loads(result)
        assert parsed['username'] == 'john'
        assert parsed['password'] == '[REDACTED]'

    def test_capture_bytes(self):
        """Should capture and redact bytes body"""
        body = b'{"username":"john","password":"secret"}'
        result = capture_request_body(body, 'application/json')
        assert result is not None
        import json
        parsed = json.loads(result)
        assert parsed['username'] == 'john'
        assert parsed['password'] == '[REDACTED]'

    def test_non_json_content_type(self):
        """Should return None for non-JSON content type"""
        body = {'data': 'test'}
        result = capture_request_body(body, 'text/html')
        assert result is None

    def test_disabled(self, monkeypatch):
        """Should return None when capture is disabled"""
        monkeypatch.setenv('OTEL_CAPTURE_REQUEST_BODY', 'false')
        body = {'username': 'john'}
        result = capture_request_body(body, 'application/json')
        assert result is None

    def test_empty_body(self):
        """Should return None for empty body"""
        result = capture_request_body(None, 'application/json')
        assert result is None

    def test_invalid_json_string(self):
        """Should return None for invalid JSON string"""
        body = 'not valid json'
        result = capture_request_body(body, 'application/json')
        assert result is None

    def test_complex_nested(self):
        """Should handle complex nested structures"""
        body = {
            'user': 'john',
            'credentials': {
                'password': 'secret',
                'apiKey': 'key123'
            },
            'profile': {
                'email': 'john@example.com',
                'settings': {
                    'token': 'abc'
                }
            }
        }
        result = capture_request_body(body, 'application/json')
        assert result is not None
        import json
        parsed = json.loads(result)
        assert parsed['user'] == 'john'
        assert parsed['credentials']['password'] == '[REDACTED]'
        assert parsed['credentials']['apiKey'] == '[REDACTED]'
        assert parsed['profile']['email'] == 'john@example.com'
        assert parsed['profile']['settings']['token'] == '[REDACTED]'
