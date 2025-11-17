# AI-Agent × NotionDB アーキテクチャ要件定義書

- **Document ID:** AI-Agent-NotionDB-Architecture
- **Version:** 1.0
- **Last Updated (JST):** 2025-11-07 11:37
- **Author:** chanjun3

## 1. 概要（Overview）
本ドキュメントは、policy-tracker-ai システムにおいて、  
AIエージェントが思考プロセス（仮説・反論・展開など）を記録・学習するための  
NotionDB構成設計およびデータスキーマ統一要件を定義する。

目的は、AIエージェント間でデータをシームレスに受け渡し（JSON連携）し、  
各エージェントが独立した知識ストレージを持ちつつ、  
最終的に「統合的な知的エコシステム」を形成すること。

## 2. 背景（Background）
policy-tracker-ai では、ニュース・政策・業界情報を自律的に収集・要約・分析するAIエージェント群を運用している。  
これらのエージェントは、それぞれ異なる認知フェーズと出力構造を持つため、  
単一DBでの一元管理では、思考のトレーサビリティが損なわれる。  
そのため、各エージェントが専用のNotionDBを持ち、JSONスキーマを統一してAPI経由で双方向連携する構成を採用する。

## 3. システム構成概要（System Architecture Overview）
```mermaid
graph TD
  A[PlannerAgent DB] --> Z[Master Knowledge Index DB]
  B[CriticAgent DB] --> Z
  C[CoderAgent DB] --> Z
  D[ReviewerAgent DB] --> Z
  E[ResearchAgent DB] --> Z
  Z --> V[VectorDB / RAG再学習層]
各エージェントDB：独自の思考ログを保持（Notion API連携）

Master Index DB：各DBのメタ情報を集約し、検索・再学習を効率化

VectorDB層：全体の知識をEmbedding化し、再推論素材として活用

4. エージェント別 NotionDB 要件
エージェント    フェーズ    主目的    記録内容    対応スキーマ
PlannerAgent    思考初期化    ゴール定義とタスク計画    問いの定義・目的・優先度    planner_payload_schema.json
CriticAgent    仮説再評価    前提の反転と代替仮説生成    仮説・再構成・代替前提    critic_payload_schema.json
CoderAgent    言語化構成    思考構造の明示化    chain-of-thought・Mermaid因果構造    coder_payload_schema.json
ReviewerAgent    反論統合    批判的視点からの再評価    反論・再構成・信頼度    reviewer_payload_schema.json
ResearchAgent    展開創出    新しい仮説・テーマの創出    emergent questions・知識拡張    research_payload_schema.json

5. データ連携構造（Data Flow）
5.1 YAML × JSON の統合モデル
層    役割    ファイル例
YAML層    ワークフロー定義（処理順序）    .codex/config.yaml
JSON層    各エージェント出力（データ内容）    .codex/json_schema/*.json
DB層    永続的知識ストレージ    各Agent専用NotionDB

mermaid
コードをコピーする
graph TD
  Y[YAML Workflow] --> J[JSON Payloads]
  J --> N[NotionDB]
  N --> V[VectorDB]
6. JSONスキーマ統一方針（Schema Standardization Policy）
6.1 統一ルール
**キー名（Key）**は全エージェント共通化（title, summary, category, confidence, timestamp）

**値の型（Type）**はNotionのプロパティ型に対応

**出力構造（Structure）**はフェーズごとに部分拡張

NotionDBのプロパティ名 = JSONキー名 とする

6.2 サンプル構造
JSON出力例

json
コードをコピーする
{
  "title": "AI活用方針改訂",
  "summary": "政府がAI透明性指針を発表",
  "category": "DigitalPolicy",
  "confidence": 0.91,
  "source": "Digital Agency RSS",
  "timestamp": "2025-11-07T09:00:00Z"
}
対応する NotionDB プロパティ

プロパティ    型    内容
Title    Title    記事タイトル
Summary    Text    要約
Category    Select    分類タグ
Confidence    Number    信頼度
Source    URL/Text    出典情報
Timestamp    Date    日付・時刻

7. 運用要件（Operational Requirements）
項目    内容
同期方式    Codex SDK または Function Calling によるAPI連携
同期頻度    各エージェント処理完了時（リアルタイム）
エラー対応    notion_sync_status（pending / synced / failed）で管理
履歴管理    各DB出力を VectorDB に定期バックアップ
バージョン管理    version フィールドで構造更新を追跡

8. メリットと期待効果（Expected Outcomes）
分離型DB構成のメリット

思考履歴のトレーサビリティ向上

各エージェントの再学習独立性

Codex SDKによるデータ整合性検証

NotionDBが“AI研究ノート”として機能

システム全体効果

PlannerAgentがMaster DBで統合し、知見を組織的に再利用

JSON共通化により、RAG学習や自動要約処理へスムーズ移行

9. 今後の開発タスク（Next Steps）
タスク    内容    優先度
① notion_db_map.yaml 作成    各AgentのDB IDマッピング    ★★★
② JSONスキーマ生成    各Agent専用スキーマファイル作成    ★★☆
③ Notion連携テスト    API通信・同期動作確認    ★★☆
④ VectorDB連携    全体知識の再学習層構築    ★☆☆

10. まとめ（Summary）
本設計により、policy-tracker-ai は以下を実現する：

各AIエージェントが独立して思考・記録できる知的モジュール化構造

NotionDBを中核とした自己進化型ナレッジネットワーク

YAML×JSON連携による行動と記憶の統一構造

💡 AIが思考し、Notionが記憶し、Codexが整合性を保つ。
これが、chanjun3流「自己進化型エージェントアーキテクチャ」の完成形である。
