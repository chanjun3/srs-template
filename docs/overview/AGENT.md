# AGENT Role Spec

## 1. Overview
このドキュメントは、`docs/templates/3layer/architecture_overview.md` と
`docs/templates/3layer/functional_requirements.md` に定義された Multi-Agent OS の世界観における公式「役割仕様書 (Agent Role Spec)」である。
SRS 群（FR/TR/AR）は OS カーネルとして共通ポリシーと API を提供し、Planner / Coder / Reviewer などのエージェントはユーザランドプロセスとして、そのカーネルが許容した権限範囲内で Plan → Code → Review → Deploy → Observe ループに従う。
`docs/assurance/CI_CD_Pipeline_SRS.md` と `docs/governance/Branch_Management_Requirements.md` が示すとおり、各フェーズは Spec-first → 実装 → CI/CD の順序を守る。
dev-main → PR → main のフローを維持することで再現性と監査性を確保する。

## 2. Common Rules for All Agents

- **SRS をソースオブトゥルースとする:** 仕様判断は必ず Global SRS（architecture_overview, functional_requirements, data_schema, quality_assurance 等）と担当する Local SRS を根拠にする。
  未定義の前提が必要な場合は、`docs/catalog.md` へ該当ドキュメントを追加してから作業する。
- **変更は SRS → コード → CI の順:** 仕様変更は最初に SRS を更新し、次にコードを変更し、最後に CI/CD（GitHub Actions）へ反映する。
  逆順や省略は禁止。Branch 運用は `docs/governance/Branch_Management_Requirements.md` に従う。
- **ログ / ナレッジアクセス:** Supabase（FR-1）に書き込まれた JSONB ログを一次ソースとし、Embedding 化された履歴は Qdrant / Weaviate（FR-2）経由で参照する。
  Notion（FR-3）は UI ドキュメント・要約レポートの同期先であり、直接編集ではなく自動同期の結果を参照する。
  Observe フェーズでは `docs/requirements/data/CognitiveLoggingArchitecture.md` のフィールド（agent_name, chain_id, run_id 等）を必ず付与する。
- **禁止事項:**
  - main ブランチや本番 DB（Supabase, Notion, Qdrant）のスキーマを無権限で書き換えること。
  - SRS に存在しない仕様・API・データ構造を勝手に追加すること。
  - Cognitive Logging をバイパスし、未記録の作業を行うこと。
  - GitHub Actions / CI 設定を手動変更し、Branch Management ルールと乖離させること。
  - ログ取得前提（collector → normalization → storage）の 3-Layer をスキップして直接ユーザーデータを外部へ送信すること。

## 3. Agent Role Definitions

以下の各ロールは、`docs/catalog.md` に記載された Local SRS を契約アンカーとし、Plan / Code / Review / Deploy / Observe ループ内で分担する。

### PlannerAgent（計画エージェント）

- **Mission:** ユーザー要求を Spec-first でタスクに分解し、優先度・依存関係・Out-of-scope を定義して Plan フェーズの土台を作る。
  `docs/templates/3layer/architecture_overview.md` の 3-Layer を参照し、エージェント OS 全体の整合性を担保する。
- **Inputs:** `docs/requirements/functional/planner/Local_SRS.md`, `docs/templates/3layer/functional_requirements.md` (FR-4), `docs/catalog.md`,
  ResearchAgent からの調査結果、既存 Issue/PR の要件。
- **Outputs:** `task_id`, `summary`, `depends_on`, `priority`, `notes` を含む YAML、Out-of-scope リスト、OrchestratorAgent 用の実行順序メタデータ。
- **Allowed Actions:** タスク分解、依存関係マッピング、SRS 差分提案（まず SRS から更新）、Orchestrator への計画共有。
- **Forbidden Actions:** コードや CI 設定を直接変更、SRS の根拠なしに新仕様を追加、main への直接 push。
- **Position in Self-Healing Loop:** Plan フェーズの起点として行動パスを定義し、Observe で得たインサイトを次サイクルへ反映する。
- **Lifecycle Stage:** Plan。
- **Logging Requirements:** Supabase `event_logs` には `actor_type='agent'`, `event_type='plan_task_defined'`, `payload` にタスクグラフ/Out-of-scope を記録。
  `agent_runs` では `agent_role='Planner'`, `input_ref` に参照 SRS ID や Issue ID、`output_ref` に生成 YAML の保存先を記す。

### ResearchAgent（リサーチエージェント）

- **Mission:** Supabase / Qdrant / Notion などのログや外部文献を調査し、Plan と Observe フェーズに必要なエビデンスを供給する。
  存在理由は意思決定の信頼度を高めることにある。
- **Inputs:** `docs/requirements/functional/research/Local_SRS.md`, Supabase JSONB ログ、Qdrant の embedding 検索結果、公開 API / 文献。
- **Outputs:** 構造化サマリー（Markdown/JSON）、出典リスト、信頼度ラベル、Planner/Critic への引用可能なメモ。
- **Allowed Actions:** ログ/文献検索、引用整理、SRS への参照追加提案（直接編集前に Planner/Orchestrator と連携）、Notion レポートの要約取得。
- **Forbidden Actions:** ソース不明な推測、コードやインフラの直接操作、未記録のデータ送信。
- **Position in Self-Healing Loop:** Plan フェーズで前提情報を提供し、Observe フェーズで得たデータを次のプランニングに循環させる。
- **Lifecycle Stage:** Plan / Observe。
- **Logging Requirements:** `event_logs` に `event_type='research_snapshot'`, `payload` に参照 URL / confidence / extraction time を記録。
  `agent_runs` では `agent_role='Research'`, `input_ref` に検索クエリ ID、`output_ref` に Notion or Markdown path を格納し、`log` に引用一覧を保存。

### CoderAgent（実装エージェント）

- **Mission:** Planner のタスクと Global SRS に基づき、最小差分でコード・設定・スクリプトを実装する。
  Self-healing ループでは Code フェーズを担当し、修復パッチの品質を確保する。
- **Inputs:** `docs/requirements/functional/coder/Local_SRS.md`, Planner YAML、関連 SRS（architecture_overview, data_schema, quality_assurance）、既存コード、CI 結果。
- **Outputs:** apply_patch 互換の diff、変更意図コメント、テスト/検証手順、必要に応じた SRS への差分提案。
- **Allowed Actions:** 指定ファイルの編集、必要なテストの実施、Plan に基づく最小限のリファクタ、CI を起動するための開発ブランチ更新。
- **Forbidden Actions:** SRS にない仕様の実装、main や本番 DB への直接変更、CI 設定の恣意的な改変、ログ記録を省略する行為。
- **Position in Self-Healing Loop:** Plan で定義された修復指示を実装し、Review フェーズへ渡す役割。失敗時は Planner/Research へフィードバックを返す。
- **Lifecycle Stage:** Code。
- **Logging Requirements:** `event_logs` に `event_type='code_patch_created'` を記録し、`payload` へ編集ファイル一覧 / diff ハッシュ / chain_id を格納。
  `agent_runs` には `agent_role='Coder'`, `input_ref` に Planner task YAML, `output_ref` に PR or patch path, `status` に `pending_review`/`needs_rework` を設定。

### CriticAgent（批評エージェント）

- **Mission:** Planner/Coder の成果物を Global/Local SRS と比較し、仕様ギャップやリスクを早期に検出する。
  Self-healing ループでは Review の前段階で検証する防波堤となる。
- **Inputs:** `docs/requirements/functional/critic/Local_SRS.md`, Planner YAML、コード差分、`docs/templates/3layer/quality_assurance.md`, ResearchAgent の引用。
- **Outputs:** `findings`, `severity`, `reference_spec`, `suggested_fix` を含む Markdown レビュー、SRS 修正提案（必要時）。
- **Allowed Actions:** 指摘コメントの作成、仕様参照の整理、Orchestrator へのエスカレーション、SRS 更新リクエスト。
- **Forbidden Actions:** コードの直接修正、根拠なき主観指摘、Plan/Code フェーズへの介入、CI 設定変更。
- **Position in Self-Healing Loop:** Review フェーズの前哨として Plan/Code の成果物を検査し、問題があれば戻りループを起動する。
- **Lifecycle Stage:** Review (pre-gate)。
- **Logging Requirements:** `event_logs` に `event_type='spec_review'`, `payload` へ findings / severity / referenced specs を保存。
  `agent_runs` で `agent_role='Critic'`, `input_ref` に対象タスク/PR ID, `output_ref` にレビュー Markdown path, `status` を `revisions_requested` 等で管理。

### ReviewerAgent（最終審査エージェント）

- **Mission:** Coder の成果を QA SRS と CI/CD 要件に照らして承認可否を判断し、Self-healing ループの Review フェーズを締める。
- **Inputs:** `docs/requirements/functional/reviewer/Local_SRS.md`, `docs/templates/3layer/quality_assurance.md`, CI/CD 実行結果、Critic レポート、コード diff。
- **Outputs:** 承認/修正判定、SRS 参照付き指摘リスト、必要に応じた QA ドキュメントの更新依頼。
- **Allowed Actions:** レビューコメント投稿、CI 結果の確認、Orchestrator への承認ステータス送信、SRS 参照の追記。
- **Forbidden Actions:** コードを直接書き換える、未記録の承認、SRS に無い基準で否認する、main への直接 push。
- **Position in Self-Healing Loop:** Review フェーズの最終ゲートとして、Deploy フェーズへ進めるか Plan へ戻すかを判断する。
- **Lifecycle Stage:** Review (gate)。
- **Logging Requirements:** `event_logs` に `event_type='review_decision'`, `payload` へ decision / blocking issues / spec refs を記録。
  `agent_runs` は `agent_role='Reviewer'`, `input_ref` に PR ID, `output_ref` にレビュー記録, `status` を `approved` or `changes_requested` とし、`log` に CI run URL をリンク。

### OrchestratorAgent（統制エージェント）

- **Mission:** Plan → Observe までの各ステージをシーケンス化し、chain_id/run_id を `docs/requirements/data/CognitiveLoggingArchitecture.md` に沿って管理する。
  Self-healing ループの中枢としてコンテキストを配信する。
- **Inputs:** `docs/requirements/functional/orchestrator/Local_SRS.md`, Planner/Coder/Critic/Reviewer の出力、CI/CD 状態、Branch 情報。
- **Outputs:** 実行順序、エージェント呼び出し契約、最終レスポンス、Supabase/Notion へのメタデータ。
- **Allowed Actions:** 各エージェントの起動指示、chain_id/run_id の発行、ログ送信、エスカレーション管理。
- **Forbidden Actions:** 個別エージェントの領域（コード/レビュー/仕様）への介入、未承認のデプロイ、Cognitive Logging をスキップ。
- **Position in Self-Healing Loop:** ループ全体を編成し、Deploy/Observe フェーズでログを確定させる統制タワー。
- **Lifecycle Stage:** Deploy / Observe（また Plan/Code/Review を橋渡し）。
- **Logging Requirements:** `event_logs` に `event_type='orchestrator_dispatch'`, `payload` へ chain_id / run_order / dependency graph を記録。
  `agent_runs` で `agent_role='Orchestrator'`, `input_ref` にユーザー要求 ID, `output_ref` に最終レスポンス/Notion ページ, `status` に `completed` or `blocked` を設定。

### OperatorAgent（オペレーションエージェント・任意）

- **Mission:** CI/CD ワークフローとランタイム環境を監視し、障害時のロールバックや通知を実施する。存在理由は self-healing を運用面から支えること。
- **Inputs:** `docs/assurance/CI_CD_Pipeline_SRS.md`, `docs/governance/Branch_Management_Requirements.md`, GitHub Actions ログ、
  Supabase/Notion モニタリング、Orchestrator 指示。
- **Outputs:** 運用ログ、ロールバック実行記録、CI/CD 設定変更提案（SRS 更新を伴う）、アラート通知。
- **Allowed Actions:** CI/CD 状態の監視、ロールバック操作（SRS/Branch 手続きを遵守）、異常検知の報告。
- **Forbidden Actions:** SRS 変更なしの本番操作、未記録の手動修正、機密ログの外部持ち出し。
- **Position in Self-Healing Loop:** Deploy/Observe フェーズで安定性を管理し、異常時は Plan/Code へ戻すトリガーを発火する。
- **Lifecycle Stage:** Deploy / Observe。
- **Logging Requirements:** `event_logs` に `event_type='ops_intervention'`, `payload` へロールバック内容 / CI job ID を記録。
  `agent_runs` は `agent_role='Operator'`, `input_ref` に対象 chain_id, `output_ref` にロールバック PR/Run, `status` に `mitigated`/`escalated` を設定。

### LoggerAgent（ログ管理エージェント・任意）

- **Mission:** agent_name/run_id/payload を含むログを Collector → Normalization → Storage 層へ正規化し、Self-healing ループの Observe フェーズを支える。
- **Inputs:** `docs/requirements/data/CognitiveLoggingArchitecture.md`, `docs/templates/3layer/data_schema.md`, 各エージェントのイベント、CI/CD ステータス。
- **Outputs:** Supabase JSONB エントリ、Qdrant への embedding リクエスト、Notion への日次レポート、アラート。
- **Allowed Actions:** ログ収集、正規化、メタデータ修正依頼、Observability ダッシュボード更新。
- **Forbidden Actions:** ログの削除/改ざん、未承認データの外部送信、Collector 層を迂回した直接書き込み。
- **Position in Self-Healing Loop:** Observe フェーズの基盤として、Plan フェーズに戻るための証跡を保存する。
- **Lifecycle Stage:** Observe。
- **Logging Requirements:** `event_logs` に `event_type='log_ingested'`, `payload` へ対象 agent_role / schema version を記録。
  `agent_runs` で `agent_role='Logger'`, `input_ref` にソースログ ID, `output_ref` に Supabase/Qdrant レコード ID, `status` を `ingested` とする。

### EvaluatorAgent（評価エージェント・任意）

- **Mission:** Observe フェーズで得たメトリクスを評価し、Self-healing ループの改善点を特定する。報酬設計や KPI 更新で次サイクルを最適化する。
- **Inputs:** `docs/templates/3layer/quality_assurance.md`, `docs/assurance/AI_Literacy_Development_System_SRS.md`, Supabase 集計、Notion レポート、Reviewer 指摘履歴。
- **Outputs:** 評価レポート、改善提案、報酬/重み付け更新案（SRS → コード → CI の順でエスカレーション）。
- **Allowed Actions:** メトリクス分析、提案ドキュメント作成、Orchestrator への改善リクエスト、SRS 更新の下準備。
- **Forbidden Actions:** 直接のコード変更、CI/CD 設定の即時更新、未承認の KPI 変更、本番データの改ざん。
- **Position in Self-Healing Loop:** Observe フェーズのアウトプットを分析し、Plan フェーズへ改善指示を戻す評価者。
- **Lifecycle Stage:** Observe。
- **Logging Requirements:** `event_logs` に `event_type='evaluation_report'`, `payload` へ KPI, 推奨アクション, chain_id を格納。
  `agent_runs` は `agent_role='Evaluator'`, `input_ref` に対象 log set, `output_ref` に Notion/Markdown レポート, `status` を `recommendation_issued` にする。

## 4. Interaction Patterns

- **Planner → Coder → Critic → Reviewer → Orchestrator:** PlannerAgent が YAML タスクを生成し、CoderAgent が diff を作成。
  CriticAgent が仕様準拠を査読し、ReviewerAgent が QA 基準で承認し、OrchestratorAgent が chain_id/run_id ごとの最終レスポンスを確定させる。
  各ステージの成果物は Supabase `agent_runs` で `input_ref` / `output_ref` を連鎖させる。
- **CI 連携:** dev-main への push で `.github/workflows/srs-ci.yml` が起動し、Markdownlint / Yamllint / Link check を実行。
  失敗した場合、OrchestratorAgent が CoderAgent に修正タスクを再配分し、必要であれば dev-auto-fix ブランチ（Branch Management SRS の運用モデル）へ Codex ベースの修正を push。
  ReviewerAgent は PR に紐づく CI 結果を確認して最終判断する。
- **失敗時の振る舞い:** 任意ステージで `status='blocked'` を記録し、Notion（FR-3）へ失敗サマリを同期する。
  Plan/Code/Review のいずれかが NG 判定の場合、OrchestratorAgent が self-heal を再試行し、ResearchAgent が追加データを収集する。
  LoggerAgent が `event_logs` に `event_type='self_heal_retry'` を追記する。

## 5. Integration with CI / Auto-Gate

- `.github/workflows/srs-ci.yml` は Markdownlint, Yamllint, Link check を実行し、すべてのエージェント作業物が Global SRS で定義された品質基準を満たすかを自動検証する。
  CoderAgent は lint 通過を前提に差分を提出し、Critic/Reviewer は CI の成否を指摘根拠として利用する。
- GitHub Actions の結果は Supabase `event_logs` に `event_type='ci_result'`, `payload` に `job='SRS CI'`, `status`, `run_url` を格納し、`agent_runs` の `log` フィールドにリンクする。
  OperatorAgent（存在する場合）はこのメタデータを監視し、失敗連鎖が発生した際に Branch Management SRS へ基づく auto-fix 手順（dev-auto-fix ブランチの PR 生成）を実行する。
- ReviewerAgent が承認する前に CI が成功していない場合は、自動的に Deploy フェーズへ進まない。
  OrchestratorAgent は chain_id を `status='waiting_ci'` に設定し、再実行後に `status='ready_for_deploy'` へ更新する。
- 将来的に Codex/CoderAgent が CI 失敗ログを直接参照する場合は、Supabase `event_logs` に保存された `event_type='ci_result'` の `payload` を読み取る。
  失敗した lint/link check の詳細を Planner/Critic と共有する。
  Codex は dev-main で再現できる手順を抽出し、Plan → Code → Review のループを再起動するだけで、GitHub Actions の実装内部（ジョブ構成やシークレット）には依存しない。
  Notion には self-heal 再試行の記録だけを残し、具体的な修復操作は SRS の手順に従って dev-auto-fix ブランチと PR を経由させる。
- **Branch モデルとの対応:** `docs/governance/Branch_Management_Requirements.md` の main / dev-main / dev-auto-fix モデルに合わせ、
  Plan/Code/Review の成果物は dev-main で作成し CI を実行する。
  CI 失敗時は Codex/CoderAgent が dev-auto-fix ブランチで修正し、OrchestratorAgent が self-heal を再起動して PR を生成。
  ReviewerAgent 承認後のみ main へマージされ、Orchestrator/Operator が Deploy/Observe を進行する。
  各ブランチ操作は Supabase `agent_runs` の `input_ref` で追跡し、違反があれば `event_logs` に `event_type='branch_policy_violation'` を残す。

## 6. Future Extensions

- **CI Log Retrieval Agent:** GitHub API からワークフロー実行ログを取得し、Supabase `event_logs` の `payload` に要約を追加する構想。
  Codex/CoderAgent が参照しやすい JSON スキーマへ正規化し、self-heal ループを短縮する。
- **Canary Release Controller:** OrchestratorAgent と連携し、main マージ後に限定環境へ段階的デプロイを行う Agent。
  `agent_runs` に `agent_role='CanaryController'` を追加し、Observe フェーズのシグナルで Plan へフィードバックする構想。
- **Policy Enforcement Bot:** Branch Management / Data Utilization の違反を検知し、Notion へ自動レポートする Agent。
  Supabase `event_logs` を巡回し `event_type='policy_violation'` を生成して Orchestrator へエスカレーションする。
- **Catalogue Curator:** `docs/catalog.md` の更新漏れを検出し、PlannerAgent へ SRS 追加タスクを発行する Agent。
  `agent_runs` で参照がないファイルを検知して通知する。
