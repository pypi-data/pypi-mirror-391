"""stdout/stderr 민감정보 자동 마스킹 구현."""

import sys
import threading
from contextlib import contextmanager

from .patterns import SensitivePatterns


class RedactingStreamWrapper:
    """stdout/stderr를 래핑하여 민감정보 자동 마스킹."""

    def __init__(self, original_stream):
        self.original_stream = original_stream
        self._patterns = SensitivePatterns.get_compiled()
        self._error_count = 0

    def _may_contain_sensitive(self, text: str) -> bool:
        """키워드 기반 빠른 민감정보 체크."""
        text_lower = text.lower()
        return any(
            keyword in text_lower for keyword in SensitivePatterns.TRIGGER_KEYWORDS
        )

    def write(self, text: str) -> int:
        try:
            # Fast path: 민감정보 키워드가 없으면 그대로 출력
            if not self._may_contain_sensitive(text):
                return self.original_stream.write(text)

            # Slow path: 패턴 매칭 및 마스킹
            sanitized = text
            for pattern, replacement in self._patterns:
                # re.sub()는 replacement가 문자열이든 함수든 자동으로 처리
                sanitized = pattern.sub(replacement, sanitized)

            return self.original_stream.write(sanitized)
        except Exception as e:
            # 에러 발생 시 출력 차단 (보안 우선 - fail-closed)
            self._error_count += 1
            if self._error_count >= 10:
                # 치명적 오류: redaction 비활성화 (무한 에러 방지)
                sys.stdout = self.original_stream
                return self.original_stream.write(text)
            return self.original_stream.write("***REDACTION_ERROR***\n")

    def flush(self):
        """원본 스트림에 flush 위임."""
        return self.original_stream.flush()

    def __getattr__(self, name):
        """나머지 메서드는 원본 스트림에 위임."""
        return getattr(self.original_stream, name)


# 재진입 방지를 위한 thread-local 상태
_redaction_state = threading.local()


def _setup_multiprocess_redaction():
    """멀티프로세스 환경에서 자식 프로세스에 redaction 전파 (UNIX only)."""
    import os

    # UNIX 계열 시스템에서만 fork 후 redaction 적용
    if hasattr(os, "register_at_fork"):
        os.register_at_fork(after_in_child=_apply_redaction_in_child)


def _apply_redaction_in_child():
    """자식 프로세스에서 redaction 재적용."""
    if not isinstance(sys.stdout, RedactingStreamWrapper):
        sys.stdout = RedactingStreamWrapper(sys.stdout)
    if not isinstance(sys.stderr, RedactingStreamWrapper):
        sys.stderr = RedactingStreamWrapper(sys.stderr)


@contextmanager
def redacted_logging_context():
    """
    stdout/stderr에 민감정보 자동 마스킹 적용.

    컨텍스트 매니저로 사용하며, 재진입 안전(thread-safe)합니다.
    UNIX 시스템에서는 fork 후 자식 프로세스에도 자동 전파됩니다.

    Examples:
        >>> with redacted_logging_context():
        ...     print("AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
        AWS_ACCESS_KEY_ID=***ENV_VAR_xxxx***

    """
    # 재진입 방지
    if getattr(_redaction_state, "active", False):
        yield
        return

    _redaction_state.active = True
    _setup_multiprocess_redaction()

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        sys.stdout = RedactingStreamWrapper(original_stdout)
        sys.stderr = RedactingStreamWrapper(original_stderr)
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        _redaction_state.active = False


def sanitize_exception(exc: Exception) -> str:
    """
    예외 메시지에서 민감정보 마스킹.

    Args:
        exc: 마스킹할 예외 객체

    Returns:
        마스킹된 예외 메시지 문자열

    Examples:
        >>> exc = ValueError("Key: AKIAIOSFODNN7EXAMPLE")
        >>> sanitize_exception(exc)
        'Key: ***AWS_KEY_xxxx***'

    """
    error_str = str(exc)

    # 모든 패턴 적용 (re.sub()가 문자열/함수 자동 처리)
    for pattern, replacement in SensitivePatterns.get_compiled():
        error_str = pattern.sub(replacement, error_str)

    return error_str
