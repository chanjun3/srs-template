# Functional Requirements：3層データ基盤

## FR-1 Supabase Functional Requirements
### FR-S1 ログ保存
- Agent SDK / Codex の出力を JSONB 形式で保存する。

### FR-S2 メタデータ管理
- token使用量、モデル名、実行時間、エージェント種別を保持。

### FR-S3 API接続
- PythonおよびPowerShellから直接POST可能。
- GitHub Actionsからも接続可能。

### FR-S4 集計
- 日次・週次でエージェント稼働状況を集計する関数を提供。

---

## FR-2 Qdrant / Weaviate Functional Requirements
### FR-V1 Embedding化
- Supabaseのログをembedding化し、Qdrantに保存。

### FR-V2 類似検索
- 過去のエラー、修正パターン、仕様書要素を検索できること。

### FR-V3 自己修復支援
- Agent SDK が行動前に「似たエラー」検索を行えること。

### FR-V4 Docker化
- ローカル・Linuxサーバ双方で起動可能なDocker構成を提供。

---

## FR-3 Notion Functional Requirements
### FR-N1 UIドキュメント管理
- SRS、設計書、アーキテクチャ概要をNotionに保存。

### FR-N2 自動同期
- Supabase集計データをNotion DBに反映する。

### FR-N3 ナレッジ構造化
- 修復履歴、改善ログをNotionページとしてタグ分類。

---

## FR-4 エージェント行動ループ仕様
(1) Supabaseログ保存  
(2) Embedding生成 → Qdrantへ送信  
(3) 類似検索で過去事例を参照  
(4) Plan → Code → Deploy  
(5) 実行結果をSupabaseへ保存  
(6) Notionへ要約レポートを生成

---

## FR-5 GitHub Actions連携
- 毎日 AM3:00 に Supabase → Notion 同期ジョブを実行。
- Push時にSupabaseバックアップを作成。
