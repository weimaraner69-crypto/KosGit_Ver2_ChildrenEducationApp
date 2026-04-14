"""学習セッションサンプル CLI のテスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.run_learning_session import (
    build_sample_lesson,
    build_sample_session,
    format_result,
    main,
)

from my_package.domain.learning import evaluate_learning_session

if TYPE_CHECKING:
    from pytest import CaptureFixture


def test_sample_lesson_and_session_match() -> None:
    """サンプルレッスンとセッションを採点できる。"""
    lesson = build_sample_lesson()
    session = build_sample_session("Aoi")

    result = evaluate_learning_session(lesson, session)

    assert result.lesson_id == "hiragana-basic-1"
    assert result.learner_name == "Aoi"
    assert result.total_questions == 3
    assert result.answered_questions == 3
    assert result.correct_answers == 2


def test_format_result_contains_score_summary() -> None:
    """整形結果にスコアと詳細が含まれる。"""
    result = evaluate_learning_session(
        build_sample_lesson(),
        build_sample_session("Ren"),
    )

    output = format_result(result)

    assert "learner: Ren" in output
    assert "score: 2/3 (66.7%)" in output
    assert "q2: NG" in output


def test_main_prints_result(capsys: CaptureFixture[str]) -> None:
    """main は結果を標準出力へ表示して終了コード0を返す。"""
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "lesson_id: hiragana-basic-1" in captured.out
    assert "score: 2/3 (66.7%)" in captured.out
