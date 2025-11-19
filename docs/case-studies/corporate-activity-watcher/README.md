# 🧾 System Requirements Specification  
**Module:** Corporate Activity Watcher Agent  
**Author:** jun1_  
**Date:** 2025-10-30  
**Version:** 1.0  

---

## 1️⃣ 概要（Overview）

Corporate Activity Watcher Agent は、  
企業の**具体的な行動（投資・雇用・研究・政策連携など）**をモニタリングし、  
その動きが株価や景気トレンドに与える影響を定量的に解析するAIモジュール。

本モジュールは、IR開示・特許情報・求人データ・設備投資動向を自動収集し、  
**「好調企業がどのように行動しているか」**を学習し、  
未来の成長セクターを予兆として捉える。

---

## 2️⃣ システム目的（Purpose）

| 目的 | 説明 |
|------|------|
| 🔍 企業行動の自動トラッキング | 決算・IR・特許・採用など、企業の“動き”を構造化データに変換 |
| 💡 株価との連動分析 | 株価上昇企業と共通する行動パターンを抽出 |
| 🧠 行動シグナルの学習 | 「どんな行動が株価上昇を生むか」をAIが学習 |
| 🔗 ValuationFeedbackAnalyzer連携 | 行動→株価→再行動の循環構造を統合解析 |

---

## 3️⃣ 機能要件（Functional Requirements）

### (1) データ収集
- TDnet / EDINET：決算短信・IRニュース
- 特許庁API：出願・登録情報
- Indeed / LinkedIn：求人・雇用動向
- 経産省 / 補助金ポータル：政策連携・助成金採択情報
- SNSモニタリング：企業PR活動の頻度とトーン分析

### (2) LLM要約・意味解析
- IR文書・ニュースを自然言語解析し、以下のカテゴリに分類：
  - **Investment（投資・設備）**
  - **Research（研究・特許）**
  - **Employment（雇用・採用）**
  - **Policy Collaboration（国策連携）**
  - **Finance（資金・自社株買い）**
- JSON形式で要約を出力。

### (3) 行動指標の生成
| 指標名 | 内容 |
|---------|------|
| **ActivityIntensity** | 行動量の総合スコア（出願件数・IR回数・求人件数） |
| **InnovationMomentum** | 特許・新製品発表の勢い |
| **EmploymentExpansion** | 雇用・給与水準の変化率 |
| **PolicyConnectivity** | 政策・助成金との関連度 |
| **CorporateSentiment** | LLMによるPR・IRのトーン分析結果 |

### (4) 出力フォーマット例
```json
{
  "company": "ソニーグループ",
  "activity_intensity": 0.85,
  "innovation_momentum": 0.91,
  "employment_expansion": 0.78,
  "policy_connectivity": 0.67,
  "corporate_sentiment": "Positive",
  "insight": "AI研究強化と海外投資拡大が株価上昇の主要要因。"
}

4️⃣ データモデル（Schema）
フィールド名    型    説明
date    date    データ取得日
company    text    企業名
sector    select    業種カテゴリ
activity_intensity    number    総合行動スコア
innovation_momentum    number    研究・特許関連スコア
employment_expansion    number    雇用変化率
policy_connectivity    number    政策連携度
corporate_sentiment    select    Positive / Neutral / Negative
stock_return_3m    number    株価3ヶ月後のリターン
insight    rich text    AI要約コメント
5️⃣ モジュール構成（Architecture）
CorporateActivityWatcherAgent/
 ├─ collector.py            # 各データソースからの収集
 ├─ parser.py               # LLMによる意味分類
 ├─ analyzer.py             # 行動パターン抽出・株価連動分析
 ├─ notion_sync.py          # NotionDB反映
 └─ config.yaml             # 閾値・スケジュール設定

6️⃣ ビジネス応用（Use Cases）
活用対象    目的
💹 投資AI    好調企業と同じ行動パターンを示す“次の上昇候補”を抽出
🏢 経営者    成功企業の行動を参考に自社戦略を最適化
🧩 政策分析    政府支援と企業活動の連動を可視化
🧠 知識資産化    AIが行動事例を自動ナレッジとして蓄積（RAG連携）
7️⃣ 連携先と拡張

🔗 ValuationFeedbackAnalyzer：行動→株価フィードバックを解析

🔗 MacroSignal Intelligence System：マクロ経済要因と結合

📊 NotionDB連携：企業行動履歴の蓄積・スコア可視化

⚙️ Reinforcement Trainer：行動パターンを報酬関数へ転用

8️⃣ 根拠と展望（Rationale）

株価上昇企業は実体経済でも先行的に動いていることが多く、
その行動パターンを学習することで“次の勝ち組”を予兆できる。

IRや求人など定性的データも、LLM解析により定量化が可能。

本モジュールは、企業の“行動の匂い”から市場シグナルを抽出する知能として機能する。

✨ 終章（Vision）

「企業の行動は、未来の市場を語る言葉である。」

Corporate Activity Watcher Agent は、
経済の動的変化を“行動のパターン”として読み解く
新しいタイプの知能である。
