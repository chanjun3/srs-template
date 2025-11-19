# Integration Requirements

## IR-1 Supabase ↔ Qdrant
- Supabaseのログをembedding化 → Qdrantへ送信するPythonバッチを提供。

## IR-2 Qdrant ↔ AgentSDK
- PlannerAgentが行動前に類似検索を行うAPIフックを設置。

## IR-3 Supabase ↔ Notion
- 集計結果をNotion APIでアップロード。

## IR-4 GitHub Actions
- 「ログ同期」「embedding生成」「Notion反映」の3ジョブ構成。

## IR-5 CI/CD
- テスト環境はSQLite＋Qdrantローカルで代替可能。
