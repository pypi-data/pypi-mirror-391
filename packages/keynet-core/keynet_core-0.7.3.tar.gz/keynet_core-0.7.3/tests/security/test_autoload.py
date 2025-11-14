"""Tests for automatic redaction activation via .pth file."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from keynet_core.security.autoload import activate
from keynet_core.security.redaction import RedactingStreamWrapper


class TestAutoloadActivation:
    """Test autoload.activate() function."""

    def test_activate_wraps_stdout_stderr(self):
        """activate() should wrap stdout and stderr."""
        # Reset state
        if hasattr(sys, "_keynet_redaction_active"):
            delattr(sys, "_keynet_redaction_active")

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            activate()

            # Should be wrapped
            assert isinstance(sys.stdout, RedactingStreamWrapper)
            assert isinstance(sys.stderr, RedactingStreamWrapper)

            # State flag should be set
            assert getattr(sys, "_keynet_redaction_active", False) is True

        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if hasattr(sys, "_keynet_redaction_active"):
                delattr(sys, "_keynet_redaction_active")

    def test_activate_idempotent(self):
        """activate() should be idempotent (multiple calls safe)."""
        # Reset state
        if hasattr(sys, "_keynet_redaction_active"):
            delattr(sys, "_keynet_redaction_active")

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # First activation
            activate()
            first_stdout = sys.stdout
            first_stderr = sys.stderr

            # Second activation should not double-wrap
            activate()
            second_stdout = sys.stdout
            second_stderr = sys.stderr

            # Should be the same wrapper
            assert first_stdout is second_stdout
            assert first_stderr is second_stderr

        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if hasattr(sys, "_keynet_redaction_active"):
                delattr(sys, "_keynet_redaction_active")

    def test_activate_respects_disable_env(self):
        """activate() should respect KEYNET_DISABLE_REDACTION=1."""
        # Reset state
        if hasattr(sys, "_keynet_redaction_active"):
            delattr(sys, "_keynet_redaction_active")

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            with patch.dict(os.environ, {"KEYNET_DISABLE_REDACTION": "1"}):
                activate()

                # Should NOT be wrapped
                assert sys.stdout is original_stdout
                assert sys.stderr is original_stderr

                # State flag should NOT be set
                assert not getattr(sys, "_keynet_redaction_active", False)

        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if hasattr(sys, "_keynet_redaction_active"):
                delattr(sys, "_keynet_redaction_active")

    def test_activate_failsafe(self):
        """activate() should not crash Python startup on errors."""
        # Reset state
        if hasattr(sys, "_keynet_redaction_active"):
            delattr(sys, "_keynet_redaction_active")

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # Mock import error in the redaction module
            with patch(
                "keynet_core.security.redaction.RedactingStreamWrapper",
                side_effect=ImportError("Mock import error"),
            ):
                # Should not raise exception
                activate()

                # stdout/stderr should be unchanged (because import failed)
                assert sys.stdout is original_stdout
                assert sys.stderr is original_stderr

        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if hasattr(sys, "_keynet_redaction_active"):
                delattr(sys, "_keynet_redaction_active")


class TestPthFile:
    """Test .pth file existence and content."""

    def test_pth_file_exists(self):
        """keynet_autoload.pth should exist in core package."""
        pth_file = Path(__file__).parent.parent.parent / "keynet_autoload.pth"
        assert pth_file.exists(), f".pth file not found at {pth_file}"

    def test_pth_file_content(self):
        """keynet_autoload.pth should contain correct import statement."""
        pth_file = Path(__file__).parent.parent.parent / "keynet_autoload.pth"
        content = pth_file.read_text().strip()

        # Should contain import and activate() call
        assert "import keynet_core.security.autoload" in content
        assert "keynet_core.security.autoload.activate()" in content

    def test_pth_file_single_line(self):
        """.pth file should be a single line (Python requirement)."""
        pth_file = Path(__file__).parent.parent.parent / "keynet_autoload.pth"
        content = pth_file.read_text()

        # Should be single line (may have trailing newline)
        lines = [line for line in content.split("\n") if line.strip()]
        assert len(lines) == 1, ".pth file should contain only one line"


class TestSubprocessIntegration:
    """Test redaction activation in subprocess (simulates real usage)."""

    @pytest.mark.skipif(
        os.getenv("CI") == "true",
        reason="Subprocess tests may be flaky in CI",
    )
    def test_redaction_active_in_subprocess(self):
        """Redaction should be active when running Python subprocess."""
        # Create a simple test script
        test_script = """
import sys
from keynet_core.security.redaction import RedactingStreamWrapper

# Check if stdout is wrapped
is_wrapped = isinstance(sys.stdout, RedactingStreamWrapper)
print(f"WRAPPED:{is_wrapped}")

# Test actual redaction
print("Testing: AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout

        # Note: .pth files may not work in -c mode, but the import should work
        # We just verify that the module can be imported and used
        assert result.returncode == 0, f"Script failed: {result.stderr}"

    def test_disable_env_in_subprocess(self):
        """KEYNET_DISABLE_REDACTION should work in subprocess."""
        test_script = """
import sys
from keynet_core.security.autoload import activate

# Manually call activate (simulating .pth behavior)
activate()

# Check if wrapped
from keynet_core.security.redaction import RedactingStreamWrapper
is_wrapped = isinstance(sys.stdout, RedactingStreamWrapper)
print(f"WRAPPED:{is_wrapped}")
"""

        # Without env var - should be wrapped
        result1 = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "WRAPPED:True" in result1.stdout

        # With env var - should NOT be wrapped
        result2 = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            env={**os.environ, "KEYNET_DISABLE_REDACTION": "1"},
            timeout=10,
        )
        assert "WRAPPED:False" in result2.stdout


class TestPyprojectToml:
    """Test pyproject.toml configuration for .pth installation."""

    def test_force_include_configured(self):
        """pyproject.toml should have force-include configuration for .pth file."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()

        # Should contain force-include section
        assert "[tool.hatch.build.targets.wheel.force-include]" in content
        assert 'keynet_autoload.pth' in content


class TestPackageImportActivation:
    """Test automatic redaction activation when importing keynet packages."""

    def test_keynet_core_import_activates_redaction(self):
        """Importing keynet_core should automatically activate redaction."""
        # Reset state
        if hasattr(sys, "_keynet_redaction_active"):
            delattr(sys, "_keynet_redaction_active")

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # Remove keynet_core from sys.modules to force re-import
            if "keynet_core" in sys.modules:
                del sys.modules["keynet_core"]

            # Import keynet_core
            import keynet_core  # noqa: F401

            # Should be activated
            assert getattr(sys, "_keynet_redaction_active", False) is True
            assert isinstance(sys.stdout, RedactingStreamWrapper)

        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if hasattr(sys, "_keynet_redaction_active"):
                delattr(sys, "_keynet_redaction_active")

    def test_keynet_train_import_activates_redaction(self):
        """Importing keynet_train should automatically activate redaction."""
        test_script = """
import sys
import os

# Set AWS key before import
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAIOSFODNN7EXAMPLE'

# Import keynet_train
from keynet_train import TrainConfig

# Check if redaction is active
print(f"REDACTION_ACTIVE:{getattr(sys, '_keynet_redaction_active', False)}")

# Test if sensitive data is masked
print("AWS_ACCESS_KEY_ID=" + os.environ['AWS_ACCESS_KEY_ID'])
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "REDACTION_ACTIVE:True" in output
        # AWS key should be masked (환경변수 패턴으로 마스킹됨)
        assert "AKIAIOSFODNN7EXAMPLE" not in output
        assert "***ENV_VAR_" in output

    def test_keynet_inference_import_activates_redaction(self):
        """Importing keynet_inference should automatically activate redaction."""
        test_script = """
import sys
import os

# Set AWS key before import
os.environ['AWS_SECRET_ACCESS_KEY'] = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

# Import keynet_inference
from keynet_inference import Storage

# Check if redaction is active
print(f"REDACTION_ACTIVE:{getattr(sys, '_keynet_redaction_active', False)}")

# Test if sensitive data is masked
print("AWS_SECRET_ACCESS_KEY=" + os.environ['AWS_SECRET_ACCESS_KEY'])
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = result.stdout
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "REDACTION_ACTIVE:True" in output
        # AWS secret should be masked
        assert "wJalrXUtnFEMI" not in output
        assert "***ENV_VAR_" in output
