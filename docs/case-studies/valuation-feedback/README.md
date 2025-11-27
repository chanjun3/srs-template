# 🧾 System Requirements Specification  

**Module:** Valuation Feedback Analyzer  
**Author:** jun1_  
**Date:** 2025-10-30  
**Version:** 1.0  

---

## 1️⃣ 概要（Overview）

Valuation Feedback Analyzer は、  
「株価上昇 → 資金調達力向上 → 企業活動強化 → 成果 or 期待の再評価」  
という市場の**自己増幅ループ（Reflexivity）**を定量的に観測するAIモジュールである。

本モジュールは、企業行動データ・IR情報・株価トレンド・資金調達履歴を解析し、  
**“株価が企業行動に与える実行力の影響”**を可視化・学習することを目的とする。

---

## 2️⃣ システム目的（Purpose）

| 目的 | 説明 |
|------|------|
| 💹 株価の反射性解析 | 株価変動と企業活動（投資・雇用・R&D等）の関係を時系列で分析 |
| 🧠 実行力スコア化 | 株価上昇に伴う資金余力や実行能力をAIが推定 |
| 🔍 成果の質判定 | 「実体を伴う成長」か「期待先行の熱狂」かを分類 |
| 🔗 MacroSignal連携 | 政策・実体経済・株価モジュールとの相関分析を統合 |

---

## 3️⃣ 機能要件（Functional Requirements）

### (1) データ収集

- EDINET / TDnet より決算・有報データ取得
- yfinance より株価・出来高データ取得
- 特許庁API・求人API（Indeed等）から企業活動指標を補足
- e-Stat / IMF データと統合（景気との関連）

### (2) 指標生成

| 指標名 | 説明 |
|---------|------|
| **ValuationMomentum** | 株価のトレンド強度と継続性 |
| **FundingLeverage** | 株価上昇に伴う調達余力の変化 |
| **ExecutionCapacity** | 設備投資・雇用・R&Dの伸び率から算出 |
| **OutcomeVariance** | 投資結果と業績変化の乖離 |
| **ReflexivityIndex** | 株価→行動→成果→株価のループ強度 |

### (3) 学習・解析

- LLMが企業ニュースを意味解析し、活動カテゴリを分類（投資／研究／採用／M&A）
- XGBoost / LSTM による株価と企業行動の相関モデリング
- 強化学習モデルで「期待 vs 実体」の報酬構造を学習

### (4) 出力形式

JSON構造で以下を出力：

```json
{
  "company": "例：三菱重工業",
  "valuation_momentum": 0.82,
  "execution_capacity": 0.91,
  "outcome_variance": 0.12,
  "reflexivity_index": 0.78,
  "classification": "実体伴う拡張フェーズ",
  "insight": "株価上昇により防衛関連設備投資が加速し、政策支援と連動。"
}

## 4️⃣ データモデル（Schema）

フィールド名    型    内容
date    date    解析日
company    text    企業名
sector    select    防衛・半導体・エネルギーなど
stock_price    number    終値
funding_ratio    number    自己資本比率 or 調達規模
execution_capacity    number    投資・雇用・R&Dスコア
reflexivity_index    number    株価と企業行動の相互影響度
classification    select    実体拡張 / 期待先行 / 成果乖離
insight    text    AI生成の分析コメント

## 5️⃣ ビジネス応用（Use Cases）

分野    活用例
💹 投資判断    株価上昇企業の中から「行動の裏付けがある銘柄」を抽出
🧭 経営戦略    自社・競合の資金余力と投資行動をモニタリング
🏦 政策分析    国策セクター内で“株価主導型成長”を検出
🧩 RAG連携    「過去に似た企業行動を示したケース」をAIが照合して示唆生成
## 6️⃣ モジュール構成

ValuationFeedbackAnalyzer/
 ├─ collector.py                # 企業行動・IR・株価データ収集
 ├─ analyzer.py                 # 指標生成・相関分析
 ├─ model_trainer.py            # LSTM / RL モデル学習
 ├─ notion_sync.py              # NotionDB反映
 └─ config.yaml                 # スケジュール・閾値設定

## 7️⃣ 根拠と展望（Rationale）

ソロスの「反射性理論」に基づき、市場と企業行動の双方向性をAIで定量化。

実体経済との接続により、MacroSignalシステム全体の判断精度を高める。

将来的には、企業行動→株価反応→景気波及を統合した強化学習モデルへ発展させる。

## 8️⃣ 成果物出力

📊 NotionDB「Corporate Intelligence DB」へ自動登録

🧩 RAG対応形式で「知識資産」として保存

📑 SRSテンプレート配下に markdown 要件として蓄積

## ✨ 終章（Vision）

「株価は企業の通信簿ではなく、
未来の行動計画書である。」

Valuation Feedback Analyzer は、
期待と実体のギャップを測る知能として、
経済の“意志”を理解するための羅針盤となる。

## Reference

- docs/spec_os/srs.md
