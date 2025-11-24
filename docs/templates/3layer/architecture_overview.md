Architecture Overview
1. Purpose

このドキュメントは、srs-template プロジェクトにおけるアーキテクチャの「共通の頭の中」を定義するためのものです。

2. Background
2.1 SRS-first な前提

このリポジトリは「SRS がソースコードよりも先に存在する」という前提で動きます。

SRS = 仕様書というより OS のカーネル 的なもの

各機能 / サービスごとに Local SRS

全体の振る舞いポリシー標準をまとめる Global SRS

コードインフラエージェントは、基本的に SRS に書かれたことだけを正当化 します。
この思想の延長で Multi-Agent OS を組み立てるのが本ドキュメントの背景です。

2.2 3-Layer Architecture の前提

データ & ログ基盤は、ざっくり以下の 3 層に切るのが定石です。

Collector Layer

イベントログメトリクスを「とにかく落とさず取る」層

Normalization Layer

カオスな入力を、意味のある共通スキーマに整形する層

Storage & Analysis Layer

クエリしやすく保存し、分析モニタリング自動化に使う層

Multi-Agent OS から見ると、この 3 層は 「現実世界の状態を観測するためのセンサ」 です。
逆に 3 層から見ると、Multi-Agent OS は 「観測結果に応じて自動アクションを起こすコントローラ」 になります。

3. Industry 3-Layer Architecture (A)
3.1 Collector Layer
3.1.1 役割

アプリ / サービス / 外部 API / エージェント から

イベント

ログ

メトリクス

を 一元的に収集 する入口レイヤー

3.1.2 入力 / 出力

Input

アプリケーションログ (JSON line, text)

トランザクションイベント（注文、ジョブ開始/終了 など）

エージェントアクション (Planner のプラン生成、Coder のパッチ提案 など)

Output

ストリーミングイベント（キュー / PubSub / Webhook）

生ログ（オブジェクトストレージ / Supabase 一時テーブル）

3.1.3 コンポーネント例

アプリからの HTTP/Webhook エンドポイント

SDK / Logging ライブラリ

Queue / PubSub（例: Kafka / Cloud PubSub 相当のもの）

Ingestion Lambda / Worker

3.1.4 設計ガイドライン（どう動くべきか）

少なくとも 1 回届ける (at-least-once) ことを優先し、重複は後段で潰す方針

Collector は「薄く安定」を最優先にし、ビジネスロジックを埋め込まない

イベント名フィールド名は SRS の Event 定義 に寄せる

仕様にないイベントを追加する場合は、必ず SRS から更新する

Multi-Agent のアクションも 必ずイベント化（誰がいつ何をなぜやったか）

3.1.5 別視点（DX 観点）

Developer Experience 的には、Collector は

「とりあえず log_event() 叩けば OK」

「フォーマットとか宛先は気にしなくていい」

という 雑に投げても破綻しない API を目指すと、導入コストがめちゃ下がる

3.2 Normalization Layer
3.2.1 役割

Collector から飛んでくる バラバラのフォーマット / 品質のデータ を

スキーマを決める

タイムゾーン型ID を揃える

PII をマスキングトークナイズする

といった処理で 分析と自動化に耐えうる形 に整えるレイヤ

3.2.2 入力 / 出力

Input

Raw event stream

生ログファイル

Output

正規化済みイベントテーブル（Supabase）

正規化済みメトリクス

Qdrant に投入可能なドキュメント（テキスト + メタ情報）

3.2.3 コンポーネント例

ETL / ELT ジョブ

スキーマ変換ツール（JSON Schema, Avro など）

PII マスキング / ハッシュ化処理

重複排除idempotency キー処理

3.2.4 設計ガイドライン（どう動くべきか）

スキーマは SRS から生成する（手書きではなく、仕様に紐づける）

Normalization は基本的に「意味は変えず、形式だけ整える」ラインを守る

フィールドの意味単位は必ず

/docs/requirements の Domain モデル

/docs/overview の Data Flow 図
に整合するようにする

エージェントからのログも、同じく

actor_type（Planner / Coder / Human など）

context_id（SRS ID / Issue ID / Session ID）
を統一的に付与しておく

3.2.5 別視点（MLOps 観点）

後で LLM / モデルに食わせることを考えると、

「説明変数として意味がある形」か

「学習に使えるぐらいノイズが低いか」

という視点で Normalization を設計しておくと、Multi-Agent OS との親和性が高まる

3.3 Storage & Analysis Layer
3.3.1 役割

正規化されたデータを

クエリしやすい形で保存

ダッシュボード / モニタリング / アラート / 自動アクション に使えるようにする

Multi-Agent OS の観点では、ここが

Supabase Log OS (JSONB)

Qdrant Vector Retrieval

などの 状態と記憶の中枢 になる

3.3.2 入力 / 出力

Input

Normalization layer からのクレンジング済みデータ

Output

集約ビュー / マート

モニタリング用メトリクス

エージェント用の検索 API（SQL / Vector / Full-text）

3.3.3 コンポーネント例

Supabase（PostgreSQL）

イベントテーブル（JSONB）

サマリテーブル（集約）

Qdrant（ベクトルストア）

チャット履歴

SRS のセクション

PR / Issue / Runbook などのドキュメント

BI / ダッシュボードツール

Alerting / Rule Engine

3.3.4 設計ガイドライン（どう動くべきか）

書き込みパスと読み取りパスを意識して、

書き込みは柔らかく (JSONB / スキーマの後追い OK)

読み取りは固く (ビュー / マートで固定スキーマ)

エージェントが使うクエリは

なるべく プリセット化された View / Stored Procedure / API 経由

生 SQL を LLM に書かせるのは最小限に

「Storage & Analysis から見える世界 = プラットフォームの真実」なので、

ここに載らない情報に依存した自動化は極力減らす

3.3.5 別視点（プロダクト観点）

エンドユーザから見ると、このレイヤは

レポート

アナリティクス

インサイト

として見えるので、ここに載せたい指標 = 何をプロダクトの価値と定義するか という議論とセットで設計すると良い。

4. chanjun3 Multi-Agent OS Architecture (B)
4.1 OS Kernel Concept (SRS-first)
4.1.1 コンセプト

SRS = OS カーネル

ドメインモデル

ユースケース

非機能要件

プロセスポリシー

これらを「仕様書」というより システムを動かす API やシステムコール として扱う。

エージェントや CI は、SRS に書かれたことを

読み取り（read_srs()）

提案を作り（propose_change()）

レビューし（review_against_srs()）

マージする（apply_change()）

というサイクルで扱う。

4.1.2 Local SRS / Global SRS モデル

Global SRS

プロダクト全体のポリシー

共通ドメイン（ユーザ、認証、監査ログなど）

アーキテクチャ原則

Local SRS

各コンポーネント / サービスごとの仕様

ログイベント / API / データモデルなどの詳細

Multi-Agent OS は、

プランニング時：Global SRS を参照して「やっていいこと / だめなこと」を決める

実装時：対象コンポーネントの Local SRS を見て、具体的な I/F を引く

という形で両者を使い分ける。

4.2 Codex Self-Healing Loop

Codex（コード生成 LLM）を中心に、以下の 4 ステップで 自己修復ループ を回す。

Plan

Planner エージェントが SRS / Issue / ログを読み

「何をどこまでどのように変えるべきか」をタスクブレイクダウン

Code

Coder エージェントが実際のパッチを生成

既存コード / SRS / ログを context に含める

Review

Critic / Reviewer エージェントが

コード品質

SRS との整合性

セキュリティ / パフォーマンス

をチェックし、必要なら修正要求

Deploy

CI（GitHub Actions）でテスト & ポリシーチェック

Auto-Gate 条件を満たしたら自動マージ / 部分的ロールアウト

行動指針（どう運用するか）

小さなスコープでループを閉じる

1 PR で 1 機能 or 1 バグ修正に絞る

SRS から入る

まず SRS の更新  それを踏まえたコード変更、の順番を守る

エージェントの失敗もログ化

失敗した提案 / 却下された PR も Supabase / Qdrant にためて、次の精度アップに使う

4.3 Data Layer (Supabase Log OS)
4.3.1 役割

Supabase (PostgreSQL) を Log OS として扱い、

すべてのイベント

エージェントアクション

CI 結果

ユーザ操作

を JSONB 中心でタイムライン保存 する。

4.3.2 典型的なテーブルイメージ

event_logs

id

occurred_at

actor_type (user / service / agent)

actor_id

event_type

payload (JSONB)

agent_runs

id

agent_role (Planner / Coder / Critic / Reviewer / Orchestrator)

input_ref (SRS ID, Issue ID, etc.)

output_ref (PR ID, Doc ID, etc.)

status

log (JSONB)

4.3.3 設計ポイント

JSONB による柔軟さを活かしつつ、

集計に良く使うものは materialized view / 正規テーブル に切り出す

重要なイベントには SRS の ID / ドメインキー を必ず含める

「まず Supabase にログがあるか？」を、トラブルシュートの第一ステップにする

4.4 Vector Layer (Qdrant)
4.4.1 役割

Qdrant を 長期記憶 + 意味検索エンジン として使う

SRS のセクションごとの埋め込み

PR diff の要約

Issue / チャット履歴

Runbook / Incident Report

4.4.2 使われ方

Planner / Researcher が context を引くとき：

「この SRS に関連する過去の議論 / 似た修正」

「同じような障害対応の Runbook」

Coder / Critic / Reviewer が使うとき：

似たパターンの PR を引っ張って、Diff の雛形やアンチパターンを把握

4.4.3 設計ポイント

Supabase の ID と Qdrant のベクトルを 双方向にリンク しておく

コレクションは

srs_sections

code_changes

incidents

runbooks
など用途別に分ける

埋め込みの更新頻度を決めておき、

大きな SRS 変更時には再埋め込みジョブを走らせる

4.5 Knowledge Plane (Notion)
4.5.1 役割

Notion を 人間が読みやすいナレッジ平面 として扱い、

SRS のビュー

アーキ図

運用 Runbook

デシジョンログ (ADR 的なもの)

をまとめる。

4.5.2 Multi-Agent との関わり

Researcher / Planner は

Notion ページをスクレイピング or API で読み取り

要約 / Diff / 決定事項を抽出

Reviewer は

PR の説明と Notion の設計ページを突き合わせ

「仕様に対してこの変更は妥当か？」を評価

4.5.3 設計ポイント

Notion 側のページ構成を

/docs/requirements

/docs/overview
と可能な限り 1:1 対応させる

ページには必ず SRS ID / コンポーネント ID をメタデータとして埋め込む（LLM がマッチングしやすくする）

4.6 CI / Auto-Gate Layer (GitHub Actions)
4.6.1 役割

GitHub Actions を Auto-Gate として扱い、

テスト

Lint / Format

SRS 整合性チェック

セキュリティスキャン

を通過条件にすることで、人間のレビュー負荷を減らしつつ安全性を確保 する。

4.6.2 代表的な Gate

srs-check

SRS のバージョン / 参照整合性のチェック

schema-check

データスキーマと SRS の定義の差分検知

agent-log-check

エージェントが生成した PR のメタ情報が Supabase / Qdrant に記録されているか確認

policy-check

センシティブファイルの変更や、禁止パターンの検出

4.6.3 運用指針

Auto-Gate 条件を満たしている PR は

「基本自動マージ＋人間はサンプリングレビュー」

条件を満たさない PR は

Orchestrator が「どのチェックに引っかかったか」を Notion / コメントに可視化

人間 Reviewer がガチで見る

4.7 Multi-Agent Orchestration
4.7.1 ロール定義

Planner

SRS / ログ / Issue / KPI からタスクを分解

どの Local SRS / コンポーネントを触るかを決める

Researcher

Qdrant / Notion / Git 履歴からコンテキストを収集

似た事例アンチパターンを引いてくる

Coder

実際のコード / インフラ定義 / SRS の更新 PR を作る

Critic

Coder の提案をテクニカル視点でレビュー

匂い (code smell) / セキュリティ / パフォーマンス

Reviewer

SRS / プロダクト要件 / UX 観点からレビュー

必要なら Notion / SRS の更新も提案

Orchestrator

全ロールを束ねる「プロジェクトマネージャー」

どのタイミングでどのエージェントを動かすか、どこで人間にバトンタッチするかを決める

4.7.2 典型的なフロー

Orchestrator：Issue / ログ / アラートを検知

Planner：タスクを分解し、対象 SRS / コンポーネントを決定

Researcher：関連コンテキストを集めてプロンプトにまとめる

Coder：パッチ / SRS 更新案を生成

Critic：技術チェック、必要ならリトライ

Reviewer：仕様 / プロダクト観点から最終判断

CI / Auto-Gate：合格すれば自動マージ、NG なら Orchestrator に戻る

4.7.3 別視点（人間の役割）

人間は、

Gate 設計（どこまで自動にするか）
に集中し、手を動かす作業 はエージェントに寄せる のが理想。

5. Architecture Diagram (Mermaid)
graph TB

  subgraph A[3-Layer Data Pipeline]
    A1[Collector Layer]
    A2[Normalization Layer]
    A3[Storage & Analysis Layer<br/>Supabase / BI]
    A1 --> A2 --> A3
  end

  subgraph B[chanjun3 Multi-Agent OS]
    subgraph B1[OS Kernel (SRS-first)]
      Gsrs[Global SRS]
      Lsrs[Local SRSs]
      Gsrs --- Lsrs
    end

    subgraph B2[Multi-Agent Roles]
      P[Planner]
      R[Researcher]
      C[Coder]
      Cr[Critic]
      Rev[Reviewer]
      O[Orchestrator]
      P --> R --> C --> Cr --> Rev --> O
    end

    subgraph B3[Data & Knowledge Plane]
      S[Supabase Log OS (JSONB)]
      Q[Qdrant Vector DB]
      N[Notion Knowledge Plane]
      S --- Q --- N
    end

    subgraph B4[CI / Auto-Gate]
      G[GitHub Actions<br/>Tests / Policy / SRS Check]
    end

    subgraph B5[Codex Self-Healing Loop]
      Pl[Plan]
      Cd[Code]
      Re[Review]
      Dp[Deploy]
      Pl --> Cd --> Re --> Dp --> Pl
    end
  end

  %% Connections between pipeline and OS
  A3 --> S
  A3 --> Q
  B2 --> B1
  B2 --> B3
  B5 --> B2
  G --> B5
  G --> B1
  O --> G

6. Scope / Non-goals
6.1 Scope（このドキュメントがカバーすること）

3-Layer データパイプラインの 論理構造

SRS-first を前提にした Multi-Agent OS の 高レベルアーキテクチャ

Supabase / Qdrant / Notion / GitHub Actions を使った

ログ & 状態管理

ナレッジ管理

CI / Auto-Gate

Planner / Researcher / Coder / Critic / Reviewer / Orchestrator の 役割と関係

6.2 Non-goals（このドキュメントが NOT やること）

具体的なテーブル定義API 仕様（これは各 Local SRS の担当）

インフラの細かい構成（VPC, Subnet, IAM など）

モデル選定（どの LLM / Embedding モデルを使うか）

セキュリティ設計のすべて（全体方針のみで、詳細は別ドキュメント）

7. Risks & Mitigation
7.1 SRS と実装の乖離

Risk

SRS が古くなり、実装やエージェントの振る舞いとズレる

Mitigation

すべての PR に「関連する SRS セクション」を必須リンクにする

srs-check CI で SRS の更新漏れを検知

定期的な「SRS リファクタリングスプリント」を回す

7.2 エージェントの暴走 / 誤動作

Risk

Codex / エージェントが誤った変更を自動デプロイしてしまう

Mitigation

本番環境へのデプロイには必ず

人間 Reviewer の承認 or

Canary / Shadow デプロイ を経る

Supabase にすべてのエージェントアクションを記録し、ロールバック戦略を用意

Orchestrator に「安全モード（提案だけ自動マージ禁止）」を用意

7.3 ベンダーロックイン / コンポーネント変更の難しさ

Risk

Supabase / Qdrant / Notion にハードロックインし、将来の変更が難しくなる

Mitigation

SRS では「抽象インターフェース」として定義

Log OS

Vector Store

Knowledge Plane

具体プロダクトは Implementation Detail として別レイヤに分離

Export / Backup 形式を決めておき、移行パスを確保

7.4 プライバシー / コンフィデンシャリティ

Risk

ログやナレッジに機微情報が含まれ、LLM や外部サービスと連携する際にリスクになる

Mitigation

Normalization Layer で PII をトークナイズ / マスキング

Qdrant / Notion に同期する前に、公開レベルのフィルタリングを行う

SRS に「データ分類ポリシー」を明記し、Auto-Gate で違反を検知

7.5 運用複雑性

Risk

エージェントCIログベクトルナレッジとコンポーネントが増えすぎて混乱する

Mitigation

Orchestrator の可視化ダッシュボードを用意

「最初は 1〜2 ロールから導入し、徐々に増やす」段階的ロールアウト

各レイヤ / コンポーネントごとに Owner と責任範囲 を明確化

8. Versioning Rules
8.1 バージョン表記

この architecture_overview.md および関連 SRS は、以下のような SemVer 風バージョン を推奨します。

MAJOR.MINOR.PATCH

MAJOR: アーキテクチャの基本的な前提が変わる変更

例: 3-Layer を廃止して別アーキへ、Multi-Agent OS の根本構造変更

MINOR: コンポーネント追加 / ロール追加 / フロー追加など、互換性は保つが意味の拡張がある変更

例: 新しいエージェントロールの導入、追加の Auto-Gate

PATCH: 誤字修正説明改善図の軽微修正など、意味的にほぼ同じ変更

8.2 Global / Local SRS との連動

Global SRS のバージョンを Gx.y.z

Local SRS のバージョンを L<component>-a.b.c

architecture_overview.md には

対応する Global SRS バージョン

主要な Local SRS 群の最小最大バージョン

をメタデータとして記載しておく（例: front matter / 冒頭の表）

8.3 運用ルール（どう回すか）

新しいアーキテクチャ変更を提案するときは：

Issue で どのレベルの変更か (MAJOR/MINOR/PATCH) を宣言

Planner / Orchestrator が影響範囲を洗い出し

PR で SRS / 図 / Auto-Gate 設定を一括更新

リリース後は：

Notion / README / SRS のバージョン表記を揃える

Supabase / Qdrant にも「バージョンスナップショット」イベントを残しておく

以上のアーキテクチャを「デフォルトの思考フレーム」として、

新しいプロダクトを作るとき

新しいエージェントロールを追加するとき

既存システムをリファクタリングするとき

には、まずこのドキュメントと対応する SRS を開き、

どのレイヤ / ロールが関与するのかをマッピング

必要なイベント / スキーマ / Gate を洗い出し

それを満たすように Plan  Code  Review  Deploy を回す

という動き方を標準フローとして採用してください。]
