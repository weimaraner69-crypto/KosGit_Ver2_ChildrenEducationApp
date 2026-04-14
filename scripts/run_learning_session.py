#!/usr/bin/env python3
"""学習セッションのサンプル実行スクリプト。

Usage:
    uv run python scripts/run_learning_session.py
    uv run python scripts/run_learning_session.py --learner Aoi
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from my_package.core.exceptions import DomainError
from my_package.core.types import (
    AnswerSubmission,
    LearningSession,
    LearningSessionResult,
    Lesson,
    Question,
)
from my_package.domain.learning import evaluate_learning_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_sample_lesson() -> Lesson:
    """サンプル用のひらがなレッスンを返す。"""
    return Lesson(
        lesson_id="hiragana-basic-1",
        title="ひらがな はじめの3文字",
        description="『あ』『い』『う』を見分ける短い練習",
        questions=(
            Question(
                question_id="q1",
                prompt="『あ』はどれ？",
                choices=("あ", "い", "う"),
                correct_choice_index=0,
                explanation="『あ』は最初の選択肢です。",
            ),
            Question(
                question_id="q2",
                prompt="『い』はどれ？",
                choices=("え", "い", "お"),
                correct_choice_index=1,
                explanation="『い』は真ん中の選択肢です。",
            ),
            Question(
                question_id="q3",
                prompt="『う』はどれ？",
                choices=("う", "あ", "い"),
                correct_choice_index=0,
                explanation="『う』は最初の選択肢です。",
            ),
        ),
    )


def build_sample_session(learner_name: str) -> LearningSession:
    """サンプル回答を持つ学習セッションを返す。"""
    return LearningSession(
        lesson_id="hiragana-basic-1",
        learner_name=learner_name,
        answers=(
            AnswerSubmission(question_id="q1", selected_choice_index=0),
            AnswerSubmission(question_id="q2", selected_choice_index=2),
            AnswerSubmission(question_id="q3", selected_choice_index=0),
        ),
    )


def format_result(result: LearningSessionResult) -> str:
    """学習セッション結果を人が読みやすい文字列へ整形する。"""
    percentage = result.accuracy * 100
    lines = [
        f"lesson_id: {result.lesson_id}",
        f"learner: {result.learner_name}",
        f"score: {result.correct_answers}/{result.total_questions} ({percentage:.1f}%)",
        f"answered: {result.answered_questions}/{result.total_questions}",
        "details:",
    ]
    for item in result.results:
        mark = "OK" if item.is_correct else "NG"
        lines.append(
            "- "
            f"{item.question_id}: {mark} "
            f"(selected={item.selected_choice_index}, correct={item.correct_choice_index})"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """サンプル学習セッションを実行する。"""
    parser = argparse.ArgumentParser(description="学習セッションのサンプル実行")
    parser.add_argument(
        "--learner",
        default="sample-learner",
        help="学習者名（デフォルト: sample-learner）",
    )
    args = parser.parse_args(argv)

    try:
        lesson = build_sample_lesson()
        session = build_sample_session(args.learner)
        result = evaluate_learning_session(lesson, session)
    except DomainError as e:
        logger.error("学習セッション実行失敗: %s", e)
        return 1

    print(format_result(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
