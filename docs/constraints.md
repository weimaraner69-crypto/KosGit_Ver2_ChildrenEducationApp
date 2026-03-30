# 制約仕様（Constraints）

## 目的

プロジェクトの制約（安全性、品質、運用上の制限）を定義する。本ファイルは制約の仕様正本であり、実装は本ファイルに追従する。

## 制約の適用範囲

- すべての処理は、実行前に制約を評価する。
- 判断不能な場合は安全側に倒す（フェイルクローズ）。
- 制約判定は一箇所に集約し、回避できない構造にする。

## 制約一覧

> しきい値はプロジェクト固有に設定する。初期値は ADR で根拠を明記する。

### C-001 最大入力値数

| パラメータ | 値 | 備考 |
| ---------- | --- | --- |
| しきい値 | `max_values` | `PipelineConfig.max_values` で指定する |
| 初期値 | `1000` | `configs/pipeline_default.toml` の既定値 |

- 判定：`len(values) > max_values` の場合に違反とする
- 理由コード：`C001_max_values_exceeded`
- 実装箇所：`src/my_package/domain/constraints.py::_check_max_values()`
- 例外：`ConstraintViolationError(constraint_id="C-001", ...)`

#### C-001 閾値定義

| 閾値 | トリガー条件 | アクション |
| --- | --- | --- |
| `max_values - 1` | 入力値数が上限未満 | 許可 |
| `max_values` | 入力値数が上限ちょうど | 許可 |
| `max_values + 1` 以上 | 入力値数が上限超過 | `ConstraintViolationError` を送出し処理を停止 |

### C-002 有効値範囲チェック

| パラメータ | 値 | 備考 |
| ---------- | --- | --- |
| 対象 | `values[*]` | 入力値列の全要素に適用する |
| 禁止値 | `NaN`, `+inf`, `-inf` | 数値として計算不能または不安定な値を拒否する |

- 判定：各要素に対し `math.isnan(v)` または `math.isinf(v)` が真なら違反とする
- 理由コード：`C002_invalid_numeric_value`
- 実装箇所：`src/my_package/domain/constraints.py::_check_value_range()`
- 例外：`ConstraintViolationError(constraint_id="C-002", ...)`

#### C-002 閾値定義

| 閾値 | トリガー条件 | アクション |
| --- | --- | --- |
| 有限実数 | `NaN` でも `inf` でもない | 許可 |
| `NaN` | `math.isnan(v)` が真 | `ConstraintViolationError` を送出し処理を停止 |
| `+inf` / `-inf` | `math.isinf(v)` が真 | `ConstraintViolationError` を送出し処理を停止 |

## 境界値テスト方針

- `C-001` は `max_values - 1`, `max_values`, `max_values + 1` を最低限カバーする
- `C-002` は `0.0`, 負の有限値, `NaN`, `+inf`, `-inf` を最低限カバーする
- 再現性確認として、同一入力・同一設定に対して同一の処理結果が得られることを確認する
- テスト実装の正本は `tests/test_pipeline.py` とし、仕様変更時は本ファイルと同時更新する

## 状態遷移（必要な場合）

```
RUNNING ──(品質低下)──→ DEGRADED ──(制約違反/異常連鎖)──→ HALTED
   ↑                      │                               │
   └────(手動復帰)────────┘                               │
   └──────────────(手動復帰)───────────────────────────────┘
```

| 状態     | 説明     | 新規操作             |
| -------- | -------- | -------------------- |
| RUNNING  | 通常稼働 | 許可（制約評価あり） |
| DEGRADED | 品質低下 | 制限                 |
| HALTED   | 安全停止 | 禁止                 |

## 実装要件

- 制約判定は一箇所に集約し、ドメインロジックが回避できない構造にする
- 判定結果には拒否理由コードを付与する（監査ログ用）
- 制約は境界値テストを必須とする（しきい値ちょうど、直上、直下）
- 状態遷移のテストを必須とする（該当する場合）
- `check_constraints()` を制約評価の単一入口とし、`Pipeline.run()` から必ず呼び出す
- 設定値の正当性は `PipelineConfig` の不変条件で事前に検証する
- 制約違反時はフェイルクローズとして処理を継続しない

## 見直し

- しきい値は検証結果に基づき更新する
- 更新時は plan と ADR の整合を取る
- `max_values` の既定値や禁止値の扱いを変更する場合は、`configs/`, `tests/`, `docs/requirements.md` の整合を同時に確認する
