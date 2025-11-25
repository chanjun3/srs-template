# 🧾 System Requirements Specification  
## LogAnalyzerAgent – Execution Log Intelligence Module

**Document ID:** SRS-LA-001  
**Author:** jun1_  
**Date:** (更新日を記入)  
**Version:** 1.0  

---

### 1. 概要（Overview）
LogAnalyzerAgent は、各AIエージェントの実行ログを収集・解析し、  
ReinforceTrainerAgent の報酬関数入力データを生成する中核モジュール。  

OrchestratorAgent の監視下で動作し、品質・効率・安定性を定量化する。

---

### 2. 目的（Purpose）
- 各エージェントの行動履歴を時系列で構造化  
- メトリクス（成功率・遅延・コスト・品質）を自動抽出  
- 報酬関数用の入力データ（metrics.jsonl）を生成  
- 異常や逸脱パターンを検知してアラート送信  

---

### 3. 機能要件（Functional Requirements）

| 機能 | 内容 | 入出力 | 関連モジュール |
|------|------|---------|----------------|
| Log Collector | 各Agentの出力ログを収集（JSON Lines形式） | *.log / *.jsonl | Orchestrator |
| Parser | ログ構造を解析して時系列データへ変換 | raw_logs | parsed_logs |
| Metric Extractor | latency, retry, quality_score を算出 | parsed_logs | metrics.jsonl |
| Reward Preprocessor | 報酬関数に必要な特徴量を整形 | metrics.jsonl | reward_input.parquet |
| Anomaly Detector | 逸脱や失敗率上昇を検知 | metrics.jsonl | anomaly_report.md |
| Reporter | Notion / Grafana へ日次レポート送信 | metrics, anomalies | InsightWriterAgent |

---

### 4. 非機能要件（Non-Functional Requirements）
- 処理速度：1000行/秒 以上で解析可能  
- 可観測性：Prometheus エクスポートに対応 (`/metrics`)  
- 耐障害性：ログ欠損時は再スキャン（バックフィル対応）  
- データ保持：30日分をローカル保持後、RAGアーカイブへ移動  

---

### 5. データ構造（Data Schema）

#### 5.1 入力ログ構造（例）
```json
{
  "timestamp": "2025-10-30T07:00:00Z",
  "agent": "ValuationFeedbackAnalyzer",
  "workflow": "MacroSignal_Intelligence_System",
  "status": "success",
  "latency_ms": 12450,
  "tokens_in": 1823,
  "tokens_out": 654,
  "errors": [],
  "quality_score": 0.82
}

5.2 出力メトリクス構造
{
  "agent": "ValuationFeedbackAnalyzer",
  "date": "2025-10-30",
  "task_success_rate": 0.97,
  "avg_latency_ms": 11200,
  "avg_cost_per_token": 0.0023,
  "avg_quality_score": 0.84,
  "retry_count": 1
}

6. 設定ファイル（log_analyzer_config.yaml）

主要メトリクスと閾値を定義。異常検知・報酬生成に利用。

7. 出力成果物

ファイル名    内容
metrics.jsonl    各Agentの集計指標
reward_input.parquet    ReinforceTrainerAgent への入力
anomaly_report.md    異常レポート
grafana_metrics.json    ダッシュボード可視化用

8. 他モジュール連携

OrchestratorAgent：ログ取得・イベント発火

ReinforceTrainerAgent：報酬入力データ提供

InsightWriterAgent：品質レポート保存

Prometheus / Grafana：可視化連携

9. 将来拡張

LLM要約による自動説明付きレポート生成

Metric Weight 学習（どの指標が重要かを自動学習）

EventBridge 経由で複数システム間同期

