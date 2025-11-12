"""민감정보 탐지 및 마스킹 패턴 정의."""

import hashlib
import re
from typing import Callable, Optional, Union, cast


def _mask_with_hash(value: str, label: str) -> str:
    """해시 기반 마스킹 - 디버깅 가능하면서 안전."""
    hash_prefix = hashlib.sha256(value.encode()).hexdigest()[:4]
    return f"***{label}_{hash_prefix}***"


def _redact_aws_key(match: re.Match) -> str:
    """AWS Access Key 마스킹."""
    return _mask_with_hash(match.group(1), "AWS_KEY")


def _redact_keynet_credential(match: re.Match) -> str:
    """KEYNET_ prefix credential 마스킹."""
    return _mask_with_hash(match.group(1), "KEYNET_KEY")


def _redact_triton_credential(match: re.Match) -> str:
    """TRITON_ prefix credential 마스킹."""
    return _mask_with_hash(match.group(1), "TRITON_KEY")


def _redact_env_var(match: re.Match) -> str:
    """환경변수 key=value 형태 마스킹."""
    key = match.group(1)
    value = match.group(2)
    # separator 추출 (: 또는 =)
    full_match = match.group(0)
    separator = full_match[len(key) :].split(value)[0]
    masked_value = _mask_with_hash(value, "ENV_VAR")
    return f"{key}{separator}{masked_value}"


def _redact_generic_secret(match: re.Match) -> str:
    """Generic secret key=value 형태 마스킹."""
    key = match.group(1)
    value = match.group(2)
    full_match = match.group(0)
    separator = full_match[len(key) :].split(value)[0]
    masked_value = _mask_with_hash(value, key.upper())
    return f"{key}{separator}{masked_value}"


class SensitivePatterns:
    """민감정보 탐지 및 마스킹 패턴 정의."""

    TRIGGER_KEYWORDS = frozenset(
        [
            "key",
            "secret",
            "password",
            "token",
            "keynet",
            "triton",
            "mlflow",
            "rabbit",
            "app",
            "api",
            "aws",
            "access",
            "tracking",
        ]
    )

    # (regex_pattern, replacement)
    # replacement는 문자열(단순 치환) 또는 함수(동적 마스킹)
    PATTERNS = [
        # 1. AWS Access Key (프로덕션) - 해시 마스킹
        (r"\b(AKIA[0-9A-Z]{16})\b", _redact_aws_key),
        # 2. KEYNET_ prefix credential (개발/프로덕션, 3~20자 제약) - 해시 마스킹
        (r"\b(KEYNET_[A-Za-z0-9_\-]{1,13})\b", _redact_keynet_credential),
        # 3. TRITON_ prefix credential (개발/프로덕션, 3~20자 제약) - 해시 마스킹
        (r"\b(TRITON_[A-Za-z0-9_\-]{1,12})\b", _redact_triton_credential),
        # 4. Private Key - 단순 치환
        (r"-----BEGIN (RSA |PRIVATE )?KEY-----", "***PRIVATE_KEY***"),
        # 5. 환경변수 출력 (prefix 기반 + 특정 이름, 값 3~100자) - 동적 마스킹
        (
            r'(AWS_[A-Z_]+|MLFLOW_[A-Z_]+|RABBIT_[A-Z_]+|KEYNET_[A-Z_]+|TRITON_[A-Z_]+|APP_API_KEY)\s*[:=]\s*["\']?([^\s"\'\n]{3,100})(?![^\s"\'\n])',
            _redact_env_var,
        ),
        # 6. MLflow URI with credentials - 정규식 그룹 치환
        (r"(https?://)[^:]+:([^@]+)@", r"\1***:***@"),
        # 7. Generic secret pattern (3~20자 제약) - 동적 마스킹
        (
            r'\b(password|secret|token|key)\s*[:=]\s*["\']?([^\s"\'\n]{3,20})(?![^\s"\'\n])',
            _redact_generic_secret,
        ),
    ]

    _compiled_cache: Optional[list[tuple[re.Pattern, Union[str, Callable]]]] = None

    @classmethod
    def get_compiled(cls) -> list[tuple[re.Pattern, Union[str, Callable]]]:
        """컴파일된 패턴 반환 (lazy compilation + caching)."""
        if cls._compiled_cache is None:
            # mypy가 list comprehension의 타입을 제대로 추론하지 못해 cast 사용
            cls._compiled_cache = cast(
                "list[tuple[re.Pattern, Union[str, Callable]]]",
                [(re.compile(pattern), replacement) for pattern, replacement in cls.PATTERNS],
            )
        return cls._compiled_cache
