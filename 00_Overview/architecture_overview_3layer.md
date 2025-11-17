# AIエージェント基盤：3層構造アーキテクチャ概要

## 1. Purpose
本ドキュメントは、自律エージェントの運用に必要となるデータ基盤
「Supabase（構造化DB）× Qdrant/Weaviate（ベクトルDB）× Notion（UI管理）」の全体像を定義する。

## 2. Background
Codex SDK・Agent SDK のログ・履歴は指数関数的に増加する。
Notion単体運用では、保存限界・検索速度・構造化の観点でスケールしない。
そのため、ログ（機械向け）・ナレッジ（人間向け）・検索（AI向け）を三分離する必要がある。

## 3. System Overview
本システムは以下の3層で構成される：

### ① Supabase（構造化DB）
エージェントログ・実行履歴・メタデータなど全ての“生データ”を集約。

### ② Qdrant / Weaviate（ベクトルDB）
過去のログ・エラー・仕様をembedding化し、類似検索を可能にするAI脳。

### ③ Notion（UIレイヤー）
人間にとって読みやすい形の知識資産（SRS・仕様書・日報）を管理する。

## 4. Architecture Diagram (Abstract)
Agents → Supabase(logs) → Qdrant(search) → Notion(Knowledge UI)

## 5. Scope
本ドキュメントはアーキテクチャの概要を対象とし、詳細仕様は各要件ドキュメントに委譲する。
