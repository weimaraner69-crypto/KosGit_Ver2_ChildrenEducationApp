"""学習コンテンツの最小ドメインモデルと採点ロジックのテスト。"""

from __future__ import annotations

import pytest

from my_package.core.exceptions import ValidationError
from my_package.core.types import (
    AnswerSubmission,
    LearningSession,
    Lesson,
    Question,
)
from my_package.domain.learning import evaluate_learning_session


def build_lesson() -> Lesson:
    """テスト用のレッスンを返す。"""
    return Lesson(
        lesson_id="lesson-1",
        title="ひらがなクイズ",
        questions=(
            Question(
                question_id="q1",
                prompt="『あ』はどれ？",
                choices=("あ", "い", "う"),
                correct_choice_index=0,
            ),
            Question(
                question_id="q2",
                prompt="『い』はどれ？",
                choices=("え", "お", "い"),
                correct_choice_index=2,
            ),
        ),
    )


class TestLearningModels:
    """学習モデルの不変条件テスト。"""

    def test_question_requires_multiple_choices(self) -> None:
        with pytest.raises(ValidationError, match="少なくとも2件必要"):
            Question(
                question_id="q1",
                prompt="問題",
                choices=("1",),
                correct_choice_index=0,
            )

    def test_lesson_requires_unique_question_ids(self) -> None:
        question = Question(
            question_id="dup",
            prompt="問題",
            choices=("1", "2"),
            correct_choice_index=0,
        )
        with pytest.raises(ValidationError, match="一意"):
            Lesson(
                lesson_id="lesson",
                title="重複テスト",
                questions=(question, question),
            )

    def test_learning_session_requires_learner_name(self) -> None:
        with pytest.raises(ValidationError, match="learner_name は空にできない"):
            LearningSession(
                lesson_id="lesson-1",
                learner_name="",
                answers=(),
            )


class TestEvaluateLearningSession:
    """学習セッション採点のテスト。"""

    def test_evaluate_learning_session_scores_answers(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-1",
            learner_name="Aoi",
            answers=(
                AnswerSubmission(question_id="q1", selected_choice_index=0),
                AnswerSubmission(question_id="q2", selected_choice_index=1),
            ),
        )

        result = evaluate_learning_session(lesson, session)

        assert result.lesson_id == "lesson-1"
        assert result.learner_name == "Aoi"
        assert result.total_questions == 2
        assert result.answered_questions == 2
        assert result.correct_answers == 1
        assert result.accuracy == pytest.approx(0.5)
        assert result.results[0].is_correct is True
        assert result.results[1].is_correct is False

    def test_evaluate_learning_session_allows_partial_answers(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-1",
            learner_name="Ren",
            answers=(AnswerSubmission(question_id="q2", selected_choice_index=2),),
        )

        result = evaluate_learning_session(lesson, session)

        assert result.total_questions == 2
        assert result.answered_questions == 1
        assert result.correct_answers == 1
        assert result.accuracy == pytest.approx(0.5)

    def test_evaluate_learning_session_rejects_unknown_question_id(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-1",
            learner_name="Aoi",
            answers=(AnswerSubmission(question_id="q3", selected_choice_index=0),),
        )

        with pytest.raises(ValidationError, match="存在しない question_id"):
            evaluate_learning_session(lesson, session)

    def test_evaluate_learning_session_rejects_duplicate_answers(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-1",
            learner_name="Aoi",
            answers=(
                AnswerSubmission(question_id="q1", selected_choice_index=0),
                AnswerSubmission(question_id="q1", selected_choice_index=1),
            ),
        )

        with pytest.raises(ValidationError, match="一意"):
            evaluate_learning_session(lesson, session)

    def test_evaluate_learning_session_rejects_mismatched_lesson(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-2",
            learner_name="Aoi",
            answers=(),
        )

        with pytest.raises(ValidationError, match="lesson_id"):
            evaluate_learning_session(lesson, session)

    def test_evaluate_learning_session_rejects_out_of_range_choice(self) -> None:
        lesson = build_lesson()
        session = LearningSession(
            lesson_id="lesson-1",
            learner_name="Aoi",
            answers=(AnswerSubmission(question_id="q1", selected_choice_index=9),),
        )

        with pytest.raises(ValidationError, match="範囲内"):
            evaluate_learning_session(lesson, session)
