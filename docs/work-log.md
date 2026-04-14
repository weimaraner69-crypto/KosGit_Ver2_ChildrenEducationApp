# 作業ログ（Work Log）

このファイルは、会話や一時メモに依存せず作業経緯を追跡するための簡易ログである。
現在の計画は `docs/plan.md`、仕様・制約・運用ルールの正本は各 `docs/` ファイルを参照する。

## 2026-04-14: 品質基盤整備と学習ドメインモデル追加

### 目的

- `N-003 品質フレームワークの整備` に向けて、要件、制約、ポリシー、運用手順、品質ガイドを現行実装に合わせて具体化する。
- 子ども向け教育アプリ本体へ進むための最初のドメインモデルとして、学習コンテンツと学習セッション採点の最小構成を追加する。
- 壊れていたローカル `.venv` を復旧し、学習モデル追加分を再テストしてコミットする。

### 実施内容

- `project-config.yml` を実プロジェクト名と教育アプリ開発基盤の目的に合わせて具体化した。
- `docs/requirements.md` に目的、スコープ、機能要件、非機能要件、AC-050 を具体化した。
- `docs/plan.md` の `N-003` に受入条件と対象領域を追加した。
- `docs/constraints.md` に `C-001 最大入力値数` と `C-002 有効値範囲チェック` を明記した。
- `docs/policies.md` に未承認外部接続禁止、秘密情報禁止、制約最優先、フェイルクローズ、再現性証跡などを具体化した。
- `docs/runbook.md` に `uv` ベースのセットアップ、MVP パイプライン実行、ローカル品質ゲート再実行、制約違反時の復旧手順を追加した。
- `docs/quality-guide.md` を現行 CI / ローカル品質ゲートに合わせて更新した。
- `docs/architecture.md` から不要なプレースホルダーコメントを削除した。
- `Question`, `Lesson`, `AnswerSubmission`, `AnswerResult`, `LearningSession`, `LearningSessionResult` を追加した。
- `evaluate_learning_session()` を追加し、レッスンに対する回答の採点、正答数、回答数、正答率を返せるようにした。
- `tests/test_learning.py` を追加し、学習モデルの不変条件と採点ロジックをテストした。
- `.python-version` を追加し、Python 3.11 を固定した。
- `.venv` を作り直し、プロジェクト内 `.uv-python` の Python 3.11.15 を参照するよう復旧した。
- `.serena/project.yml` の Serena 設定更新を別コミットとして記録した。

### 検証結果

- `uv run ruff check src/my_package tests/test_learning.py`: 通過
- `uv run mypy src/ tests/`: 通過（20 source files）
- `uv run pytest -q --tb=short tests/test_learning.py`: 9 passed
- 品質基盤整備時の全体確認:
  - `uv run python ci/policy_check.py`: 通過
  - `uv run ruff check .`: 通過
  - `uv run mypy src/ tests/ ci/`: 通過
  - `uv run pytest -q --tb=short`: 62 passed

### 作成コミット

- `e4ec9a7` `docs: concrete N-003 quality framework`
- `7c791d0` `chore: normalize architecture doc permissions`
- `b16db72` `Normalize file permissions across the repository`
- `3d7b49b` `feat: add learning content domain model`
- `879cdda` `chore: update Serena project config`

### 現在の状態

- `master` は `origin/master` より 5 commits ahead。
- ワークツリーは、このログ追加前の時点で clean。
- `N-003` は docs とローカル品質ゲートの観点ではかなり完了に近い。

### 残件

- `docs/plan.md` の `N-003` Issue が `TBD` のまま。
- `docs/plan.md` の GitHub Project URL が未記入。
- `docs/plan.md` の Backlog がプレースホルダーのまま。
- 学習ドメインモデルを使うサンプル CLI または UI 向けデータ構造は未実装。
