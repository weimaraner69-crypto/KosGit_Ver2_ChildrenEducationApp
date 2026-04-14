"""core パッケージ — 型定義、例外、設定管理。

最下層モジュール。他のドメインモジュールに依存しない。
"""

from my_package.core.config import PipelineConfig, load_config
from my_package.core.exceptions import (
    ConfigError,
    ConstraintViolationError,
    DomainError,
    ValidationError,
)
from my_package.core.types import (
    AnswerResult,
    AnswerSubmission,
    LearningSession,
    LearningSessionResult,
    Lesson,
    PipelineInput,
    PipelineOutput,
    ProcessingResult,
    Question,
    Status,
)

__all__ = [
    "AnswerResult",
    "AnswerSubmission",
    "ConfigError",
    "ConstraintViolationError",
    "DomainError",
    "LearningSession",
    "LearningSessionResult",
    "Lesson",
    "PipelineConfig",
    "PipelineInput",
    "PipelineOutput",
    "ProcessingResult",
    "Question",
    "Status",
    "ValidationError",
    "load_config",
]
