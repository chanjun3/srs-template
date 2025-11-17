# AI-Agent Cognitive Framework SRS（思考柔軟性ワークフロー実装仕様）

- **Version:** 1.0
- **Last-Updated (JST):** 2025-11-07 10:32:01 +09:00
- **Doc-ID:** AI-Cognitive-Framework-SRS

---

## 1. 概要（Overview）

本ドキュメントは、博士課程レベルの知的ワークフローをAIエージェントへ実装するための要件を定義する。  
目的は、「思考の柔軟さと深さ」を再現し、AIが人間のように問いを立て、再構成し、進化できる知的行動ループを形成すること。

## 2. 背景（Background）

従来のAIは「知識の検索・再現」に優れていたが、  
人間のPhD的思考プロセス＝「仮説→言語化→反論→展開→再定義」という**往復運動（Recurrent Reasoning Loop）**を持たない。

本仕様は、AIエージェントに以下の４段階を組み込むことで、  
**再帰的思考（Recursive Thinking）と創発的洞察（Emergent Insight）**を両立する構造を目指す。

## 3. 機能要件（Functional Requirements）

| フェーズ | 名称 | 目的 | 実装アクション |
|---|---|---|---|
| ① 仮説再評価フェーズ（Pause & Reframe） | “ちょっと待てよ” | 既存仮説・前提の妥当性を自己検証 | - 自己生成プロンプトで前提を逆転<br>- alternative assumption生成APIを呼び出す |
| ② 言語化フェーズ（Structured Articulation） | “説明可能化” | 思考の構造を明示的に記述 | - chain-of-thoughtをJSON構造で出力<br>- 要素間の因果関係をMermaid構文で生成 |
| ③ 反論フェーズ（Dialectical Defense） | “批判的往復” | 外部視点からの反論を統合 | - internal adversarial agentで反論生成<br>- 反論→再構成→confidence updateループ |
| ④ 展開フェーズ（Forward Expansion） | “次の問い創出” | 新しい仮説・方向性を提案 | - meta-agentが次のresearch questionを生成<br>- knowledge gap detectionモジュールを起動 |

## 4. 非機能要件（Non-Functional Requirements）

- **知的柔軟性**：仮説を複数視点（倫理・社会・技術）から再構成できること  
- **透明性**：全推論過程をユーザに可視化（Why–How–What構造）  
- **メタ認知**：自己の出力に対して信頼度・曖昧性・改善提案を自動生成  
- **反復学習性**：反論・再構成の履歴を学習し、次回判断に反映すること  
- **モジュール化**：各フェーズを独立モジュールとして組み合わせ可能にする（Codex SDK連携前提）

## 5. アーキテクチャ設計（Architecture Design）

```mermaid
graph TD
A[User Input / Research Prompt]
  --> B[① 仮説再評価モジュール]
  --> C[② 言語化モジュール]
  --> D[③ 反論モジュール]
  --> E[④ 展開モジュール]
  --> F[Knowledge DB / Notion Sync]
F --> B
subgraph Cognitive Loop
  B-->C-->D-->E-->B
end
各モジュールは Codex SDK または OpenAI Function Calling 経由で独立動作。
Knowledge DB は Notion / VectorDB などを想定。履歴は再学習素材として活用。

6. 運用フェーズ（Operational Workflow）
フェーズ    担当エージェント    出力    トリガー
思考初期化    PlannerAgent    問いの定義・ゴール設定    ユーザー入力
仮説再評価    CriticAgent    前提反転・代替仮説生成    自動
言語化構成    CoderAgent    JSON / Markdown構造出力    Critic完了時
反論統合    ReviewerAgent    改善案・信頼度スコア    自動
展開創出    ResearchAgent    次の問い・方向性    Reviewer完了時

7. 期待成果（Expected Output）
再帰的思考ログ（Cognitive Trace Log）：各段階の思考プロセスを Notion DB に自動記録

反論統合型出力（Dialectical Summary）：主張＋反論＋再構成の三層出力

創発的問いリスト（Emergent Question Set）：次の研究・開発テーマ候補を抽出

8. 別視点提案（Meta-Level View）
AIエージェントがこのループを実装することで、単なる情報処理体ではなく
**「知的エコシステムの一部」**として振る舞える。
PhD試験で求められる「独立した研究者としての思考成熟度」をAIの行動設計に落とし込むと、最終的には以下が実現される👇

🧬 Self-Evolving Intelligence — AI自身が自己批判し、自己改善する思考構造体。

Change Log
2025-11-07: 初版作成（Spec v1.0）