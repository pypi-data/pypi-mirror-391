__version__ = "0.7.2"

from .security import redacted_logging_context, sanitize_exception

# 민감정보 자동 마스킹 활성화
# keynet_core를 import하는 모든 패키지에서 자동으로 보호됨
from .security.autoload import activate

activate()

__all__ = [
    "__version__",
    "redacted_logging_context",
    "sanitize_exception",
]
