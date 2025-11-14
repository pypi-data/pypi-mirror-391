"""
자동 민감정보 마스킹 활성화.

이 모듈은 keynet_autoload.pth를 통해 Python 시작 시 자동으로 실행됩니다.
K8s Job에서 `python train.py` 실행 시에도 import 순서와 무관하게 보호합니다.
"""

import sys


def activate():
    """
    Python 시작 시 redaction 자동 활성화.

    .pth 파일에서 호출되며, 다음을 수행합니다:
    1. 중복 활성화 방지 체크 (sys._keynet_redaction_active)
    2. 디버깅용 비활성화 옵션 체크 (KEYNET_DISABLE_REDACTION)
    3. stdout/stderr를 RedactingStreamWrapper로 교체
    4. 에러 발생 시에도 Python 시작은 계속 (fail-safe)
    """
    # 이미 활성화된 경우 스킵 (재진입 방지)
    if getattr(sys, "_keynet_redaction_active", False):
        return

    # 디버깅용 비활성화 환경변수 체크
    import os

    if os.getenv("KEYNET_DISABLE_REDACTION") == "1":
        return

    try:
        from keynet_core.security.redaction import RedactingStreamWrapper

        # stdout/stderr 래핑 (중복 래핑 방지)
        if not isinstance(sys.stdout, RedactingStreamWrapper):
            sys.stdout = RedactingStreamWrapper(sys.stdout)
        if not isinstance(sys.stderr, RedactingStreamWrapper):
            sys.stderr = RedactingStreamWrapper(sys.stderr)

        # 활성화 표시 (중복 방지용)
        sys._keynet_redaction_active = True  # type: ignore

    except Exception:
        # 에러 발생 시에도 Python 시작은 계속 (fail-safe)
        # redaction 실패는 로그 없이 무시 (보안 모듈이 보안 문제를 유발하면 안됨)
        pass
