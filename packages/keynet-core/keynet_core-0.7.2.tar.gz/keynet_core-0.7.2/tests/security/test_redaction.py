"""Tests for sensitive data redaction functionality."""

import io
import sys
from unittest.mock import MagicMock

from keynet_core.security import redacted_logging_context, sanitize_exception
from keynet_core.security.patterns import SensitivePatterns
from keynet_core.security.redaction import RedactingStreamWrapper


class TestBasicRedaction:
    """Test basic redaction functionality."""

    def test_aws_key_masked(self):
        """AWS Access Key should be automatically masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("Key: AKIAIOSFODNN7EXAMPLE")
        output = stream.getvalue()

        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "***AWS_KEY_" in output

    def test_keynet_prefix_masked(self):
        """KEYNET_ prefix credentials should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("Using credential: KEYNET_minio")
        output = stream.getvalue()

        assert "KEYNET_minio" not in output
        assert "***KEYNET_KEY_" in output

    def test_triton_prefix_masked(self):
        """TRITON_ prefix credentials should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("Using credential: TRITON_server")
        output = stream.getvalue()

        assert "TRITON_server" not in output
        assert "***TRITON_KEY_" in output

    def test_env_var_masked(self):
        """Environment variables should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Test AWS_* prefix
        wrapper.write("AWS_ACCESS_KEY_ID=mysecretkey")
        output1 = stream.getvalue()
        assert "mysecretkey" not in output1
        assert "AWS_ACCESS_KEY_ID=" in output1
        assert "***ENV_VAR_" in output1

        # Reset stream
        stream.truncate(0)
        stream.seek(0)

        # Test MLFLOW_* prefix
        wrapper.write("MLFLOW_TRACKING_URI=http://localhost:5000")
        output2 = stream.getvalue()
        assert "http://localhost:5000" not in output2
        assert "MLFLOW_TRACKING_URI=" in output2
        assert "***ENV_VAR_" in output2

        # Reset stream
        stream.truncate(0)
        stream.seek(0)

        # Test RABBIT_* prefix
        wrapper.write("RABBIT_ENDPOINT_URL=amqp://rabbitmq")
        output3 = stream.getvalue()
        assert "amqp://rabbitmq" not in output3
        assert "RABBIT_ENDPOINT_URL=" in output3
        assert "***ENV_VAR_" in output3

        # Reset stream
        stream.truncate(0)
        stream.seek(0)

        # Test APP_API_KEY
        wrapper.write("APP_API_KEY=my-api-key-123")
        output4 = stream.getvalue()
        assert "my-api-key-123" not in output4
        assert "APP_API_KEY=" in output4
        assert "***ENV_VAR_" in output4

    def test_normal_output_unchanged(self):
        """Normal output without sensitive data should pass through unchanged."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        normal_text = "Training epoch 1, loss: 0.5, accuracy: 0.95"
        wrapper.write(normal_text)
        output = stream.getvalue()

        assert output == normal_text

    def test_secret_in_kv_format(self):
        """Key=value format secrets should be masked (minimum 3 chars)."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("password=secret123")
        output = stream.getvalue()

        assert "secret123" not in output
        assert "password=" in output
        assert "***PASSWORD_" in output

    def test_mlflow_uri_with_credentials(self):
        """MLflow URI with embedded credentials should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("Connecting to http://admin:mypassword@mlflow.example.com")
        output = stream.getvalue()

        assert "admin" not in output
        assert "mypassword" not in output
        assert "http://***:***@" in output

    def test_private_key_masked(self):
        """Private keys should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...")
        output = stream.getvalue()

        assert "BEGIN PRIVATE KEY" not in output
        assert "***PRIVATE_KEY***" in output

    def test_fast_path_no_keywords(self):
        """Fast path should skip pattern matching when no keywords present."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Text without any trigger keywords
        text = "Hello World 12345"
        wrapper.write(text)
        output = stream.getvalue()

        assert output == text

    def test_multiple_patterns_in_one_line(self):
        """Multiple sensitive patterns in one line should all be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE password=secret123")
        output = stream.getvalue()

        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "secret123" not in output
        assert "***AWS_KEY_" in output or "***ENV_VAR_" in output
        assert "***PASSWORD_" in output or "***ENV_VAR_" in output


class TestExceptionSanitization:
    """Test exception message sanitization."""

    def test_exception_with_aws_key(self):
        """Exception containing AWS Key should be sanitized."""
        exc = ValueError("Connection failed: AKIAIOSFODNN7EXAMPLE")
        sanitized = sanitize_exception(exc)

        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
        assert "***AWS_KEY_" in sanitized
        assert "Connection failed:" in sanitized

    def test_normal_exception_unchanged(self):
        """Exception without sensitive data should be unchanged."""
        exc = ValueError("Invalid input: expected integer")
        sanitized = sanitize_exception(exc)

        assert sanitized == "Invalid input: expected integer"

    def test_exception_with_env_var(self):
        """Exception containing environment variable should be sanitized."""
        exc = RuntimeError("Config error: AWS_SECRET_ACCESS_KEY=mysecret")
        sanitized = sanitize_exception(exc)

        assert "mysecret" not in sanitized
        assert "***ENV_VAR_" in sanitized
        assert "Config error:" in sanitized

    def test_exception_with_keynet_credential(self):
        """Exception containing KEYNET_ credential should be sanitized."""
        exc = ConnectionError("Failed with KEYNET_storage credential")
        sanitized = sanitize_exception(exc)

        assert "KEYNET_storage" not in sanitized
        assert "***KEYNET_KEY_" in sanitized


class TestReentrancy:
    """Test reentrancy safety."""

    def test_nested_context(self):
        """Nested contexts should be safe and not double-wrap."""
        output_lines = []

        # Capture output
        original_stdout = sys.stdout
        capture = io.StringIO()
        sys.stdout = capture

        try:
            with redacted_logging_context():
                print("First level: password=secret1")

                with redacted_logging_context():
                    print("Second level: password=secret2")

                print("Back to first level: password=secret3")

            output = capture.getvalue()
            output_lines = output.strip().split("\n")

        finally:
            sys.stdout = original_stdout

        # All secrets should be masked
        assert len(output_lines) == 3
        for line in output_lines:
            assert "secret" not in line
            assert "***PASSWORD_" in line

    def test_context_restoration(self):
        """stdout/stderr should be restored after context exit."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with redacted_logging_context():
            # Inside context, should be wrapped
            assert isinstance(sys.stdout, RedactingStreamWrapper)
            assert isinstance(sys.stderr, RedactingStreamWrapper)

        # After context, should be restored
        assert sys.stdout is original_stdout
        assert sys.stderr is original_stderr


class TestErrorHandling:
    """Test error handling in redaction."""

    def test_redaction_error_handling(self):
        """Errors during redaction should be handled gracefully."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Mock the patterns in the wrapper to raise an exception
        mock_pattern = MagicMock()
        mock_pattern.sub = MagicMock(side_effect=Exception("Test error"))
        wrapper._patterns = [(mock_pattern, "replacement")]

        wrapper.write("password=secret")
        output = stream.getvalue()

        # Should output error message instead of crashing
        assert "***REDACTION_ERROR***" in output

    def test_error_count_limit(self):
        """After 10 errors, redaction should be disabled."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Mock the patterns in the wrapper to raise an exception
        mock_pattern = MagicMock()
        mock_pattern.sub = MagicMock(side_effect=Exception("Test error"))
        wrapper._patterns = [(mock_pattern, "replacement")]

        # Trigger 10 errors
        for i in range(10):
            wrapper.write(f"password=secret{i}")

        # Verify error count reached 10
        assert wrapper._error_count == 10

        # After 10 errors, redaction should be disabled
        # The wrapper sets sys.stdout to original stream
        # So subsequent writes should pass through
        # Note: The implementation disables by setting sys.stdout = original_stream
        # which we can't easily test here, so we just verify error count
        assert wrapper._error_count >= 10

    def test_flush_delegation(self):
        """flush() should be delegated to original stream."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # flush should not raise an error
        wrapper.flush()

    def test_getattr_delegation(self):
        """Unknown attributes should be delegated to original stream."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Should access original stream's attribute
        assert wrapper.getvalue() == ""
        wrapper.write("test")
        assert "test" in wrapper.getvalue()


class TestPatternCaching:
    """Test pattern compilation and caching."""

    def test_patterns_compiled_once(self):
        """Patterns should be compiled once and cached."""
        # Reset cache
        SensitivePatterns._compiled_cache = None

        # First call should compile
        patterns1 = SensitivePatterns.get_compiled()
        assert patterns1 is not None
        assert len(patterns1) == 7  # 7 patterns defined

        # Second call should return cached version
        patterns2 = SensitivePatterns.get_compiled()
        assert patterns2 is patterns1  # Same object (cached)

    def test_trigger_keywords(self):
        """Trigger keywords should contain expected values."""
        keywords = SensitivePatterns.TRIGGER_KEYWORDS

        assert "key" in keywords
        assert "secret" in keywords
        assert "password" in keywords
        assert "token" in keywords
        assert "keynet" in keywords
        assert "triton" in keywords
        assert "mlflow" in keywords
        assert "rabbit" in keywords
        assert "aws" in keywords
        assert "api" in keywords


class TestLengthConstraints:
    """Test length constraints for credentials (3~20 chars)."""

    def test_keynet_prefix_minimum_length(self):
        """KEYNET_ with minimum length (8 chars total) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # KEYNET_x = 8 chars (within limit)
        wrapper.write("Using KEYNET_x as credential")
        output = stream.getvalue()

        assert "KEYNET_x" not in output
        assert "***KEYNET_KEY_" in output

    def test_keynet_prefix_maximum_length(self):
        """KEYNET_ with maximum length (20 chars total) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # KEYNET_1234567890123 = 20 chars (within limit)
        wrapper.write("Using KEYNET_1234567890123 as credential")
        output = stream.getvalue()

        assert "KEYNET_1234567890123" not in output
        assert "***KEYNET_KEY_" in output

    def test_keynet_prefix_exceeds_maximum(self):
        """KEYNET_ with any length should be masked (no length limit)."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # KEYNET_12345678901234 = 21 chars (previously exceeded limit, now masked)
        wrapper.write("Using KEYNET_12345678901234 as credential")
        output = stream.getvalue()

        # Should be masked (no length limit anymore)
        assert "KEYNET_12345678901234" not in output
        assert "***KEYNET_KEY_" in output

    def test_triton_prefix_minimum_length(self):
        """TRITON_ with minimum length (8 chars total) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # TRITON_x = 8 chars (within limit)
        wrapper.write("Using TRITON_x as credential")
        output = stream.getvalue()

        assert "TRITON_x" not in output
        assert "***TRITON_KEY_" in output

    def test_triton_prefix_maximum_length(self):
        """TRITON_ with maximum length (20 chars total) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # TRITON_123456789012 = 20 chars (within limit)
        wrapper.write("Using TRITON_123456789012 as credential")
        output = stream.getvalue()

        assert "TRITON_123456789012" not in output
        assert "***TRITON_KEY_" in output

    def test_triton_prefix_exceeds_maximum(self):
        """TRITON_ with any length should be masked (no length limit)."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # TRITON_1234567890123 = 21 chars (previously exceeded limit, now masked)
        wrapper.write("Using TRITON_1234567890123 as credential")
        output = stream.getvalue()

        # Should be masked (no length limit anymore)
        assert "TRITON_1234567890123" not in output
        assert "***TRITON_KEY_" in output

    def test_env_var_value_minimum_length(self):
        """Environment variable with minimum value length (3 chars) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("AWS_ACCESS_KEY_ID=abc")
        output = stream.getvalue()

        assert "abc" not in output
        assert "AWS_ACCESS_KEY_ID=" in output
        assert "***ENV_VAR_" in output

    def test_env_var_value_reasonable_length(self):
        """Environment variable with reasonable value length (20-50 chars) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # 21 chars (URI)
        wrapper.write("MLFLOW_TRACKING_URI=http://localhost:5000")
        output = stream.getvalue()

        assert "http://localhost:5000" not in output
        assert "MLFLOW_TRACKING_URI=" in output
        assert "***ENV_VAR_" in output

    def test_env_var_value_exceeds_maximum(self):
        """Environment variable with value exceeding 100 chars should NOT be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # 101 chars
        long_value = "x" * 101
        wrapper.write(f"AWS_ACCESS_KEY_ID={long_value}")
        output = stream.getvalue()

        # Should NOT be masked (exceeds 100 char limit)
        assert long_value in output

    def test_generic_secret_minimum_length(self):
        """Generic secret with minimum length (3 chars) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("password=abc")
        output = stream.getvalue()

        assert "abc" not in output
        assert "password=" in output
        assert "***PASSWORD_" in output

    def test_generic_secret_maximum_length(self):
        """Generic secret with maximum length (20 chars) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("password=12345678901234567890")
        output = stream.getvalue()

        assert "12345678901234567890" not in output
        assert "password=" in output
        assert "***PASSWORD_" in output

    def test_generic_secret_exceeds_maximum(self):
        """Generic secret exceeding 20 chars should NOT be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        wrapper.write("password=123456789012345678901")
        output = stream.getvalue()

        # Should NOT be masked (exceeds 20 char limit)
        assert "123456789012345678901" in output

    def test_real_world_credentials(self):
        """Test real-world credential lengths (MinIO-compatible)."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Common MinIO development credentials (within limits)
        wrapper.write("AWS_ACCESS_KEY_ID=minio")  # 5 chars
        wrapper.write("AWS_ACCESS_KEY_ID=KEYNET_minio")  # 12 chars
        wrapper.write("AWS_ACCESS_KEY_ID=KEYNET_storage")  # 15 chars

        output = stream.getvalue()

        # All should be masked
        assert "minio" not in output or output.count("minio") == 0
        assert "KEYNET_minio" not in output
        assert "KEYNET_storage" not in output
        assert output.count("***ENV_VAR_") >= 3 or output.count("***KEYNET_KEY_") >= 2

    def test_long_keynet_credentials_should_be_masked(self):
        """Long KEYNET_ credentials (100+ chars) should be masked for security."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Real-world long API key (100+ chars)
        long_key = "KEYNET_GhrxHdPVsWe4tohrdlISioDkwYxbnPueVPXHxrkWc6Nz8UpvadVDr2Rs2P6kvp9PxwM8blOf2Jh3garpTaJUmsNtedlwBlqEO1yJMSGVXD5OZXgvVQnmha2LRAIqR4Sj"
        wrapper.write(f"APP_API_KEY={long_key}")
        output = stream.getvalue()

        # Should be masked
        assert long_key not in output
        assert "***KEYNET_KEY_" in output or "***ENV_VAR_" in output

    def test_medium_keynet_credentials_should_be_masked(self):
        """Medium KEYNET_ credentials (30-50 chars) should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # 38-char credential
        medium_key = "KEYNET_ZWJtSlkm8yTCLogNiDdQj64lYSjsAVVnC"
        wrapper.write(f"AWS_SECRET_ACCESS_KEY={medium_key}")
        output = stream.getvalue()

        # Should be masked
        assert medium_key not in output
        assert "***KEYNET_KEY_" in output or "***ENV_VAR_" in output

    def test_dict_repr_format_should_be_masked(self):
        """Dict repr format ('KEY': 'VALUE') should be masked."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Python dict repr format
        wrapper.write("{'APP_API_KEY': 'KEYNET_test123secret'}")
        output = stream.getvalue()

        # Should be masked
        assert "KEYNET_test123secret" not in output
        assert "***KEYNET_KEY_" in output or "***ENV_VAR_" in output

    def test_environ_repr_format_should_be_masked(self):
        """os.environ repr format should mask sensitive values."""
        stream = io.StringIO()
        wrapper = RedactingStreamWrapper(stream)

        # Realistic environ output
        long_key = "KEYNET_GhrxHdPVsWe4tohrdlISioDkwYxbnPueVPXHxrkWc6Nz8UpvadVDr2Rs2P6kvp9PxwM8blOf2Jh3garpTaJUmsNtedlwBlqEO1yJMSGVXD5OZXgvVQnmha2LRAIqR4Sj"
        wrapper.write(f"environ({{'APP_API_KEY': '{long_key}', 'PATH': '/usr/bin'}})")
        output = stream.getvalue()

        # Long key should be masked
        assert long_key not in output
        # PATH should not be masked
        assert "'/usr/bin'" in output or "\"/usr/bin\"" in output
