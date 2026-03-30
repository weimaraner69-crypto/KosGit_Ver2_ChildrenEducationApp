# 運用手順（Runbook）

## 目的

開発・検証環境を再現可能に運用し、失敗時に復旧できるようにする。

## 前提

- 秘密情報はリポジトリに含めない（P-002）
- Python 3.11 と `uv` が利用できること
- 品質チェックはローカルと CI の両方で再実行できること
- 開発中に扱う入力データはダミー値または匿名化済みデータに限定すること

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd KosGit_Ver2_ChildrenEducationApp
```

### 2. 環境の準備

#### Python (uv)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras --dev
```

### 3. 環境変数の設定

現時点の MVP パイプラインは必須の環境変数を要求しない。
今後 `.env` を導入する場合も、機密値はローカルにのみ保持し、リポジトリには含めない。

## 代表コマンド

### 静的解析

```bash
# リンター
uv run ruff check .

# フォーマッタ（チェックのみ）
uv run ruff format --check .

# 型チェック
uv run mypy src/ tests/ ci/
```

### IDE エラー検証（ゲートチェック）

CI の静的解析に加えて、IDE（Pylance 等）のエラーもゼロであることを確認する。
Copilot エージェントの場合は `get_errors` ツール（filePaths 省略）でワークスペース全体を検査する。

### テスト

```bash
# 全テスト実行
uv run pytest -q --tb=short

# カバレッジ確認
uv run pytest --cov=src --cov-report=term-missing
```

### ポリシーチェック

```bash
# 禁止操作・秘密情報検出
uv run python ci/policy_check.py
```

### MVP パイプラインの実行

```bash
# 既定設定で実行
uv run python scripts/run_pipeline.py

# 明示的に設定ファイルを指定して実行
uv run python scripts/run_pipeline.py --config configs/pipeline_default.toml
```

### ローカル品質ゲート再実行

CI 失敗の切り分けや N-003 の確認時は、次の順番で再実行する。

```bash
uv run python ci/policy_check.py
uv run ruff check .
uv run ruff format --check .
uv run mypy src/ tests/ ci/
uv run pytest -q --tb=short
```

## 生成物の扱い

| ディレクトリ | 内容               | git 管理                   |
| ------------ | ------------------ | -------------------------- |
| `outputs/`   | 実行結果、レポート | しない                     |
| `data/raw/`  | 実データ           | しない                     |
| `configs/`   | 実行設定           | する（秘密情報を含めない） |

## 失敗時対応

### CI 失敗

1. GitHub Actions のログで失敗箇所を特定する
2. ローカル品質ゲートを同じ順番で再実行する
3. 制約関連の失敗なら `docs/constraints.md` と `tests/test_pipeline.py` を確認する
4. 修正して再プッシュする

### 制約違反 (`C-001`, `C-002`)

1. 入力値数が `max_values` を超えていないか確認する
2. `NaN`, `+inf`, `-inf` が混入していないか確認する
3. `configs/pipeline_default.toml` または指定した設定ファイルを見直す
4. `uv run pytest -q --tb=short` で関連テストが通るか確認する
5. 仕様変更を伴う場合は `docs/constraints.md` と `docs/requirements.md` を同時更新する

### 設定の破損

1. `configs/pipeline_default.toml` の既定値に戻す
2. `PipelineConfig` の不変条件に違反していないか確認する
3. `uv run pytest -q --tb=short` で正常動作を確認する

### 依存関係の問題

1. `uv sync --all-extras --dev` を再実行する
2. 必要なら `uv cache clean` 後に再同期する
3. ローカル品質ゲートを再実行する

## モバイルでの開発

iPhone / iPad からの開発作業については [docs/mobile-workflow.md](mobile-workflow.md) を参照する。

## ロールバック手順

### フィーチャーブランチの巻き戻し

マージ済み PR に問題が発覚した場合、`git revert` で安全に取り消す。

```bash
# マージコミットを revert（-m 1 で first parent を指定）
git checkout main  # または master
git pull origin main
git revert -m 1 <マージコミットSHA>
git push origin main
```

**禁止事項**:

- `main` / `master` ブランチへの `git push --force` は禁止する（ブランチ保護ルール）。
- 直接コミットの修正ではなく、必ず revert コミットで対応する。

**手順**:

1. 問題のある PR のマージコミット SHA を特定する
2. `git revert -m 1 <SHA>` で revert コミットを作成する
3. CI が通ることを確認し、プッシュする
4. 必要に応じて修正 PR を別途作成する

### 本番リリースのロールバック

GitHub Releases を用いて前バージョンを特定し、ロールバックする。

**前バージョンの特定**:

```bash
# GitHub Releases の一覧を確認（最新5件）
gh release list --limit 5

# 特定リリースの詳細を確認
gh release view <タグ名>
```

**ロールバック手順**:

1. `gh release list` で前回の安定リリースのタグを特定する
2. 対象タグのコミット SHA を確認する: `git log --oneline <タグ名>`
3. production ブランチを安定コミットに巻き戻す:

   ```bash
   git checkout production
   # 安定コミット以降のコミットを確認
   git log --oneline <安定コミットSHA>..HEAD
   # ロールバック対象のコミット SHA を新しい順に列挙して revert
   git revert --no-commit <コミット1のSHA> <コミット2のSHA> ... <コミットNのSHA>
   git commit -m "fix: <タグ名> へのロールバック"
   git push origin production
   ```

4. CI / 品質ゲートの通過を確認する
5. ロールバック完了後、GitHub Release に状況を記録する:

   ```bash
   gh release create "rollback-$(date -u +%Y%m%d-%H%M%S)" \
     --title "ロールバック: <理由の要約>" \
     --notes "ロールバック先: <タグ名>、理由: <問題の詳細>"
   ```

### ポリシー違反発覚時の復旧フロー

P-001〜P-003 違反が発覚した場合の即時対応手順。

**即時停止条件**（copilot-instructions.md 参照）:

- ポリシー違反（P-001〜P-003）の検出
- 秘密情報の漏洩（P-002）
- 制約の回避・無効化（P-003）

**復旧フロー**:

1. **即時停止**: 自動実行パイプラインが稼働中の場合は即時停止する
2. **影響範囲の特定**:
   - `git log --oneline -20` で直近のコミットを確認する
   - `git diff <違反前のコミットSHA>..HEAD` で変更範囲を確認する
   - 秘密情報漏洩の場合は `git log --all -p -S '<漏洩パターン>'` で全履歴を検索する
3. **秘密情報漏洩時の追加対応**:
   - 漏洩したキー/トークンを即座に無効化（ローテーション）する
   - `git filter-repo` 等で履歴からも除去する（ADR に記録必須）
4. **違反コミットの revert**:

   ```bash
   git revert <違反コミットSHA>
   uv run python ci/policy_check.py  # ポリシーチェックで解消を確認
   ```

5. **エスカレーション**:
   - 重大な違反（秘密情報漏洩、外部への影響）はリポジトリオーナーに即時報告する
   - ADR を作成し、原因・対応・再発防止策を記録する（P-900 例外運用に準拠）
6. **再発防止**:
   - `ci/policy_check.py` のパターンに検出漏れがあれば追加する
   - ブランチ保護ルールの見直しを行う
