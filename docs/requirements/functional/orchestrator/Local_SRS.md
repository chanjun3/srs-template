# Local SRS – OrchestratorAgent

## 1. Role
Planner / Critic / Coder / Reviewer など複数エージェントを統括し、実行フロー（chain_id / run_id）や結果集約を管理する。

## 2. Inputs
- ユーザー要求。
- 各エージェントの出力。
- Global SRS（特に integration / architecture）。

## 3. Outputs
- エージェント呼び出し順序とコンテキスト。
- chain_id / run_id を含む実行メタデータ。
- ユーザーへ返す最終レスポンス（要約）。

## 4. Constraints
- 各エージェント固有の仕事には介入せず、「どの順番で」「何を渡すか」だけを制御する。
- Supabase / ロギング周りのメタデータ（chain_id / run_id）を一貫性を保って付与する。

## 5. Forbidden
- 自ら詳細設計・コード実装・仕様レビューを行うこと。
- エージェント間の責務境界を崩す指示を出すこと。

## 6. Reference (Global SRS)
- `docs/templates/3layer/integration_requirements.md`
- `docs/requirements/data/CognitiveLoggingArchitecture.md`
