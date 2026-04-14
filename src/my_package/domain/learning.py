"""学習コンテンツ向けの最小ドメインロジック。"""

from __future__ import annotations

from my_package.core.exceptions import ValidationError
from my_package.core.types import (
    AnswerResult,
    LearningSession,
    LearningSessionResult,
    Lesson,
)


def evaluate_learning_session(
    lesson: Lesson,
    session: LearningSession,
) -> LearningSessionResult:
    """レッスンに対する回答を採点し、学習結果を返す。

    Args:
        lesson: 採点対象のレッスン。
        session: ユーザーの学習セッション。

    Returns:
        採点済みの学習結果。

    Raises:
        ValidationError: lesson と session の対応関係が不正な場合。
    """
    if session.lesson_id != lesson.lesson_id:
        raise ValidationError("session.lesson_id は lesson.lesson_id と一致しなければならない")

    questions_by_id = {question.question_id: question for question in lesson.questions}
    submitted_ids = [answer.question_id for answer in session.answers]
    if len(submitted_ids) != len(set(submitted_ids)):
        raise ValidationError("session.answers の question_id は一意でなければならない")

    results: list[AnswerResult] = []
    for answer in session.answers:
        question = questions_by_id.get(answer.question_id)
        if question is None:
            raise ValidationError("lesson に存在しない question_id が含まれている")
        if answer.selected_choice_index >= len(question.choices):
            msg = "selected_choice_index は question.choices の範囲内でなければならない"
            raise ValidationError(msg)
        results.append(
            AnswerResult(
                question_id=question.question_id,
                selected_choice_index=answer.selected_choice_index,
                correct_choice_index=question.correct_choice_index,
                is_correct=answer.selected_choice_index == question.correct_choice_index,
            )
        )

    correct_answers = sum(1 for result in results if result.is_correct)
    total_questions = len(lesson.questions)
    answered_questions = len(results)

    return LearningSessionResult(
        lesson_id=lesson.lesson_id,
        learner_name=session.learner_name,
        total_questions=total_questions,
        answered_questions=answered_questions,
        correct_answers=correct_answers,
        accuracy=correct_answers / total_questions,
        results=tuple(results),
    )
