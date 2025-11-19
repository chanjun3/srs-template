# Non-Functional Requirements：3層データ基盤

## NFR-1 パフォーマンス
- embedding検索は1秒以内。
- ログ書き込みは100ms以内。

## NFR-2 スケーラビリティ
- Supabaseは100万レコードを許容。
- Qdrantは1GB〜50GBまで拡張可能。

## NFR-3 セキュリティ
- Supabase RLS 有効化。
- APIキーはGitHub Secrets管理。

## NFR-4 可観測性
- 全エージェント行動履歴が時系列でトレース可能。

## NFR-5 保守性
- Supabase・Qdrant・Notionは疎結合であること。

## NFR-6 可用性
- Docker再起動で24/7連続稼働。
