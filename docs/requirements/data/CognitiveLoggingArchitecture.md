# 40.05 Cognitive Logging Architecture Requirements  

本章では、AIエージェントの思考ログ（Cognitive Logs）を  
Supabase JSONB に保存し、再現性・可観測性・協調AI管理を実現するための  
データ要件を定義する。

---

## 1. 目的（Purpose）

AIエージェント（Planner / Coder / Reviewer / Deployer）が生成する  
プロンプト・思考過程・出力・評価メトリクスを  
**一貫した構造で Supabase に保存し、  
分析・再現・監査・最適化に耐えるデータ基盤を提供する。**

---

## 2. テーブル構造要件（JSONB）

### 2.1 cognitive_logs（必須テーブル）

必須フィールド：

- agent_name : 実行したエージェント名  
- prompt : JSONB（system / user / history を含む）  
- output : JSONB（生成結果）  
- metrics : JSONB（latency, token_usage, cost など）  
- created_at : タイムスタンプ  

任意フィールド：

- thought_chain : デバッグ時のみ保存  
- chain_id : タスク単位の識別子  
- run_id : 個別実行の識別子  

運用方針：

- JSONB により schema-less 拡張を保証  
- 必須/任意を分離して長期運用に備える  
- Downstream（DuckDB/Qdrant/RAG）が扱いやすい構造とする  

---

## 3. Multi-Agent 協調ログ要件

### 3.1 chain_id / run_id の取り扱い

- orchestrator が chain_id / run_id を付与  
- chain_id = 1タスク全体のストーリー  
- run_id = エージェント単体の1回実行  

### 3.2 分析・デバッグ目的

- Planner → Coder → Reviewer → Deployer の  
  協調実行をトレース可能  
- 故障点の特定を容易にし、  
  再現性のあるデバッグが可能  

---

## 4. ログ挙動の要件（after_run フック）

### 4.1 共通 after_run の必須化

- すべてのエージェントが after_run でログを保存  
- 保存対象構造：

{
agent_name: string,
prompt: { ... },
output: { ... },
metrics: { latency, token_usage, cost, ... },
chain_id: string,
run_id: string,
thought_chain: optional
}

yaml
コードをコピーする

### 4.2 保存コンポーネント（Saver）の要件

- retry / backoff を内部実装  
- エラー時はログ化のみで、メイン処理は停止させない  
- 将来：batching / OpenTelemetry / external sinks に拡張可能  

---

## 5. 運用（Operational Intent）

- thought_chain は debug モードのみ  
- metrics 構造（latency/token_usage/cost）は標準化  
- chain_id をキーにした dashboard/view を Supabase で構築可能  
- nightly ETL（Supabase → DuckDB → Qdrant）を前提とする  

---

## 6. 保守性・拡張性

- schema-less JSONB により migration コスト低減  
- 必須キーは固定、拡張キーは階層的に追加  
- 長期運用でも破綻しない構造を維持する  

---

@end
