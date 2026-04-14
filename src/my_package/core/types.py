"""ドメイン型定義。

プロジェクト固有のデータモデルを定義する。
すべての型は不変（frozen）データクラスで表現し、
不変条件は ``__post_init__`` で例外送出により検証する。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from my_package.core.exceptions import ValidationError


class Status(Enum):
    """パイプライン実行状態。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True)
class PipelineInput:
    """パイプラインへの入力データ。

    不変条件:
        - ``name`` は空でない。
        - ``values`` は少なくとも1要素を持つ。
    """

    name: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        """不変条件を検証する。

        Raises:
            ValidationError: 不変条件に違反する場合。
        """
        if not self.name:
            raise ValidationError("name は空にできない")
        if len(self.values) == 0:
            raise ValidationError("values は少なくとも1要素が必要")


@dataclass(frozen=True)
class ProcessingResult:
    """処理結果。

    不変条件:
        - ``count`` は正の整数。
        - ``average`` は ``total / count`` に等しい。
        - ``total`` と ``average`` は有限値。
    """

    total: float
    count: int
    average: float

    def __post_init__(self) -> None:
        """不変条件を検証する。

        Raises:
            ValidationError: 不変条件に違反する場合。
        """
        if self.count <= 0:
            msg = f"count は正の整数でなければならない: {self.count}"
            raise ValidationError(msg)
        if not math.isfinite(self.total):
            msg = f"total は有限値でなければならない: {self.total}"
            raise ValidationError(msg)
        expected_avg = self.total / self.count
        if abs(self.average - expected_avg) > 1e-9:
            msg = f"average ({self.average}) は total/count ({expected_avg}) と一致しない"
            raise ValidationError(msg)


@dataclass(frozen=True)
class PipelineOutput:
    """パイプラインの出力。

    不変条件:
        - ``status`` は SUCCESS または FAILED。
        - ``timestamp`` は UTC（tzinfo が設定されていること）。
    """

    input_name: str
    result: ProcessingResult
    status: Status
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __post_init__(self) -> None:
        """不変条件を検証する。

        Raises:
            ValidationError: 不変条件に違反する場合。
        """
        if self.status not in {Status.SUCCESS, Status.FAILED}:
            msg = f"出力の status は SUCCESS か FAILED でなければならない: {self.status}"
            raise ValidationError(msg)
        if self.timestamp.tzinfo is None:
            raise ValidationError("timestamp にはタイムゾーン情報が必須")


@dataclass(frozen=True)
class Question:
    """学習コンテンツ内の1問。

    不変条件:
        - ``question_id`` と ``prompt`` は空でない。
        - ``choices`` は2件以上の空でない選択肢を持つ。
        - ``correct_choice_index`` は ``choices`` の範囲内にある。
    """

    question_id: str
    prompt: str
    choices: tuple[str, ...]
    correct_choice_index: int
    explanation: str | None = None

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.question_id:
            raise ValidationError("question_id は空にできない")
        if not self.prompt:
            raise ValidationError("prompt は空にできない")
        if len(self.choices) < 2:
            raise ValidationError("choices は少なくとも2件必要")
        if any(not choice for choice in self.choices):
            raise ValidationError("choices に空文字は使えない")
        if not 0 <= self.correct_choice_index < len(self.choices):
            msg = "correct_choice_index は choices の範囲内でなければならない"
            raise ValidationError(msg)


@dataclass(frozen=True)
class Lesson:
    """複数の問題をまとめた学習レッスン。"""

    lesson_id: str
    title: str
    questions: tuple[Question, ...]
    description: str | None = None

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.lesson_id:
            raise ValidationError("lesson_id は空にできない")
        if not self.title:
            raise ValidationError("title は空にできない")
        if len(self.questions) == 0:
            raise ValidationError("questions は少なくとも1問必要")
        question_ids = [question.question_id for question in self.questions]
        if len(question_ids) != len(set(question_ids)):
            raise ValidationError("questions の question_id は一意でなければならない")


@dataclass(frozen=True)
class AnswerSubmission:
    """ユーザーが1問に対して送信した回答。"""

    question_id: str
    selected_choice_index: int

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.question_id:
            raise ValidationError("question_id は空にできない")
        if self.selected_choice_index < 0:
            raise ValidationError("selected_choice_index は0以上でなければならない")


@dataclass(frozen=True)
class AnswerResult:
    """1問分の採点結果。"""

    question_id: str
    selected_choice_index: int
    correct_choice_index: int
    is_correct: bool

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.question_id:
            raise ValidationError("question_id は空にできない")
        if self.selected_choice_index < 0:
            raise ValidationError("selected_choice_index は0以上でなければならない")
        if self.correct_choice_index < 0:
            raise ValidationError("correct_choice_index は0以上でなければならない")
        expected = self.selected_choice_index == self.correct_choice_index
        if self.is_correct != expected:
            raise ValidationError("is_correct は選択結果と整合していなければならない")


@dataclass(frozen=True)
class LearningSession:
    """レッスンに対する学習セッション。"""

    lesson_id: str
    learner_name: str
    answers: tuple[AnswerSubmission, ...]
    started_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.lesson_id:
            raise ValidationError("lesson_id は空にできない")
        if not self.learner_name:
            raise ValidationError("learner_name は空にできない")
        if self.started_at.tzinfo is None:
            raise ValidationError("started_at にはタイムゾーン情報が必須")


@dataclass(frozen=True)
class LearningSessionResult:
    """学習セッション全体の採点結果。"""

    lesson_id: str
    learner_name: str
    total_questions: int
    answered_questions: int
    correct_answers: int
    accuracy: float
    results: tuple[AnswerResult, ...]
    completed_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __post_init__(self) -> None:
        """不変条件を検証する。"""
        if not self.lesson_id:
            raise ValidationError("lesson_id は空にできない")
        if not self.learner_name:
            raise ValidationError("learner_name は空にできない")
        if self.total_questions <= 0:
            raise ValidationError("total_questions は正の整数でなければならない")
        if self.answered_questions < 0:
            raise ValidationError("answered_questions は0以上でなければならない")
        if self.correct_answers < 0:
            raise ValidationError("correct_answers は0以上でなければならない")
        if self.answered_questions > self.total_questions:
            raise ValidationError("answered_questions は total_questions を超えられない")
        if self.correct_answers > self.answered_questions:
            raise ValidationError("correct_answers は answered_questions を超えられない")
        expected_accuracy = self.correct_answers / self.total_questions
        if abs(self.accuracy - expected_accuracy) > 1e-9:
            raise ValidationError("accuracy は correct_answers / total_questions と一致しない")
        if len(self.results) != self.answered_questions:
            raise ValidationError("results 件数は answered_questions と一致しなければならない")
        if self.completed_at.tzinfo is None:
            raise ValidationError("completed_at にはタイムゾーン情報が必須")
