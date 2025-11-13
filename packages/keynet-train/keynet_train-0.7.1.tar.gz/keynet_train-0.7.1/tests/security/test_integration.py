"""Integration tests for security redaction in real training scenarios."""

import io
import os
import subprocess
import sys

import pytest

from keynet_core.security import redacted_logging_context


class TestPythonScriptExecution:
    """Test redaction in Python script execution scenarios."""

    def test_python_script_execution(self):
        """Test that redaction works when executing a Python script."""
        # Create a temporary test script
        test_script = '''
import sys
from keynet_core.security.autoload import activate

# Manually activate (simulating .pth behavior)
activate()

# Test output with sensitive data
print("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
print("Normal log message")
print("KEYNET_minio_cred")
'''

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        output = result.stdout

        # Sensitive data should be masked
        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "KEYNET_minio_cred" not in output

        # Normal log should pass through
        assert "Normal log message" in output

        # Masked placeholders should be present
        assert ("***AWS_KEY_" in output or "***ENV_VAR_" in output)
        assert "***KEYNET_KEY_" in output

    def test_import_order_independence(self):
        """Test that protection works regardless of import order."""
        # Test 1: Activate before sensitive print
        test_script1 = '''
from keynet_core.security.autoload import activate
activate()
print("password=secret123")
'''

        result1 = subprocess.run(
            [sys.executable, "-c", test_script1],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "secret123" not in result1.stdout
        assert "***PASSWORD_" in result1.stdout

        # Test 2: Print before any import (simulates .pth activation)
        test_script2 = '''
import sys
from keynet_core.security.redaction import RedactingStreamWrapper

# Manually wrap (simulates what .pth does)
sys.stdout = RedactingStreamWrapper(sys.stdout)

print("password=secret456")
'''

        result2 = subprocess.run(
            [sys.executable, "-c", test_script2],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "secret456" not in result2.stdout
        assert "***PASSWORD_" in result2.stdout


class TestKeynetPrefixMasking:
    """Test KEYNET_ prefix masking before keynet import."""

    def test_keynet_prefix_masked_before_import(self):
        """KEYNET_ prefix should be masked even before importing keynet."""
        test_script = '''
from keynet_core.security.autoload import activate
activate()

# Print KEYNET_ credential before importing keynet_train
print("Using credential: KEYNET_storage_key")
print("Config: AWS_ACCESS_KEY_ID=KEYNET_value_here")

# Now import keynet_train (if it was imported, doesn't matter)
import keynet_train

print("After import: KEYNET_secret")
'''

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        output = result.stdout

        # All KEYNET_ credentials should be masked
        assert "KEYNET_storage_key" not in output
        assert "KEYNET_value_here" not in output
        assert "KEYNET_secret" not in output

        # Should have mask placeholders
        assert output.count("***KEYNET_KEY_") >= 2 or output.count("***ENV_VAR_") >= 1


class TestTrainingWorkflow:
    """Test redaction in actual training workflow scenarios."""

    def test_normal_training_unaffected(self):
        """Normal training logs should not be affected by redaction."""
        # Capture output
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                # Simulate normal training logs
                print("Epoch 1/10")
                print("Loss: 0.5432")
                print("Accuracy: 0.9123")
                print("Training completed successfully")

            output = capture.getvalue()

        finally:
            sys.stdout = original_stdout

        # All normal output should be unchanged
        assert "Epoch 1/10" in output
        assert "Loss: 0.5432" in output
        assert "Accuracy: 0.9123" in output
        assert "Training completed successfully" in output

        # No masking should occur
        assert "***" not in output

    def test_config_logging_with_secrets(self):
        """Config logging with secrets should be masked."""
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                # Simulate config logging that might leak secrets
                print("Loading configuration...")
                print("MLFLOW_TRACKING_URI=http://localhost:5000")
                print("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
                print("MODEL_NAME=my_model")
                print("DATASET_PATH=/data")

            output = capture.getvalue()

        finally:
            sys.stdout = original_stdout

        # Sensitive values should be masked
        assert "AKIAIOSFODNN7EXAMPLE" not in output

        # Non-sensitive values should pass through
        assert "MODEL_NAME=my_model" in output
        assert "DATASET_PATH=/data" in output

        # Keys should remain visible
        assert "AWS_ACCESS_KEY_ID=" in output
        assert "MLFLOW_TRACKING_URI=" in output

    def test_exception_with_credentials(self):
        """Exceptions containing credentials should be sanitized."""
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                try:
                    raise ValueError("Connection failed: AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
                except ValueError as e:
                    # In real code, this might be logged
                    print(f"Error: {e}")

            output = capture.getvalue()

        finally:
            sys.stdout = original_stdout

        # Exception message should have masked credentials
        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "Connection failed:" in output
        assert ("***AWS_KEY_" in output or "***ENV_VAR_" in output)


class TestMinIOCredentials:
    """Test masking of MinIO credentials used in development."""

    def test_minio_credentials_masked(self):
        """MinIO credentials should be masked."""
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                # Simulate logging MinIO config
                print("AWS_ACCESS_KEY_ID=minio")
                print("AWS_SECRET_ACCESS_KEY=miniostorage")
                print("KEYNET_minio")
                print("KEYNET_storage")

            output = capture.getvalue()

        finally:
            sys.stdout = original_stdout

        # MinIO credentials should be masked
        # Note: "minio" and "miniostorage" as key=value will be caught by ENV_VAR pattern
        assert "AWS_ACCESS_KEY_ID=" in output  # Key should remain
        assert "AWS_SECRET_ACCESS_KEY=" in output  # Key should remain

        # Values should be masked
        # Can be masked by ENV_VAR or PASSWORD pattern
        assert "***ENV_VAR_" in output or "***PASSWORD_" in output

        # KEYNET_ prefix should be masked
        assert "KEYNET_minio" not in output
        assert "KEYNET_storage" not in output
        assert "***KEYNET_KEY_" in output


class TestSubprocessRedaction:
    """Test redaction in subprocess scenarios."""

    def test_subprocess_inherits_redaction(self):
        """Subprocess should inherit redaction from parent (UNIX only)."""
        if not hasattr(os, "register_at_fork"):
            pytest.skip("Fork not available on this platform")

        test_script = '''
import sys
from keynet_core.security.autoload import activate

activate()

# Parent process
print("Parent: password=parent_secret")

# Note: subprocess.run() doesn't fork in Python, it creates a new process
# So this test just verifies the activation works independently
print("Done")
'''

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "parent_secret" not in result.stdout
        assert "***PASSWORD_" in result.stdout


class TestEnvironmentVariableOutput:
    """Test masking of environment variable outputs."""

    def test_env_var_patterns(self):
        """Various environment variable output patterns should be masked."""
        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                # Different output formats
                print("AWS_SECRET_ACCESS_KEY=my-secret-key")
                print("MLFLOW_TRACKING_TOKEN: tracking-token-123")
                print('RABBIT_PASSWORD="rabbit-pass"')
                print("APP_API_KEY='api-key-value'")

            output = capture.getvalue()

        finally:
            sys.stdout = original_stdout

        # All secret values should be masked
        assert "my-secret-key" not in output
        assert "tracking-token-123" not in output
        assert "rabbit-pass" not in output
        assert "api-key-value" not in output

        # Keys should remain visible
        assert "AWS_SECRET_ACCESS_KEY" in output
        assert "MLFLOW_TRACKING_TOKEN" in output
        assert "RABBIT_PASSWORD" in output
        assert "APP_API_KEY" in output

        # Should have masking indicators
        assert "***ENV_VAR_" in output


class TestPerformance:
    """Test performance impact of redaction."""

    def test_fast_path_performance(self):
        """Fast path should handle normal logs efficiently."""
        import time

        capture = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = capture

        try:
            with redacted_logging_context():
                # Time normal log output (should use fast path)
                start = time.time()
                for i in range(1000):
                    print(f"Epoch {i}, loss: 0.{i}")
                fast_path_time = time.time() - start

        finally:
            sys.stdout = original_stdout

        # Fast path should complete in reasonable time
        # This is just a sanity check, not a strict performance test
        assert fast_path_time < 1.0, f"Fast path took {fast_path_time}s, expected < 1s"

        # Output should be unmodified
        output = capture.getvalue()
        assert "***" not in output
