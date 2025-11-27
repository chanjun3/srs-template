# 🧾 System Requirements Specification

**Project:** MacroSignal Intelligence System  
**Author:** jun1_  
**Date:** 2025-10-30  
**Version:** 1.0

---

## 1️⃣ システム概要（Overview）

MacroSignal Intelligence System は、実体経済データ・株価・政策ニュースを統合し、  
**「市場の反応が一時的か構造的か」**を AI が判定する経済インテリジェンス基盤。

### 1.1 目的

- リセッション／一時調整の早期識別  
- 政策インパクト（防衛・半導体・エネルギー等）の数値化  
- 投資判断・事業戦略の両面で活用できる分析パイプライン構築

---

## 2️⃣ システム目的（Purpose）

| 項目 | 内容 |
|---|---|
| 🧠 投資AIモジュール | 政策トレンド→株価→マクロ指標を学習し「市場反応の信頼度」をスコア化 |
| 💹 経済分析モジュール | 実体経済データ（雇用・生産・輸出など）を月次で可視化し、マクロトレンド検知 |
| 🏢 ビジネス応用 | 景気拡張／収縮期を検知して、営業・広告・採用タイミングを自動最適化 |

### KPI（初期）

- イベント後3日/5日リターンに対する説明力（R²）  
- 一時 vs 構造判定のF1スコア（バリデーション）  
- レポート生成のTAT（生成→配信）< 10分（週次はバッチ）  

---

## 3️⃣ システム構成（Architecture）

### 📡 Data Layer

- 政策ニュースRSS：METI / MOF / NHK ほか
- 株価データAPI：yfinance / QUICK（将来）
- 実体経済API：e-Stat / IMF / FRED
- ファンダメンタル：決算短信 / IR（HTML/PDF → 抽出）

### 🧠 Intelligence Layer

- LLM要約・意味抽出エージェント（JSON化・正規化）
- Policy–Market Impact Analyzer（イベント研究）
- Macro Lag Detector（実体経済ラグ分析）
- Recession Classifier（構造的下落判定）

### 💾 Data Store

- NotionDB（政策・業界インパクト管理、RAGメタ）
- Firestore / Supabase（時系列DB）
- BigQuery（マクロ統合分析／将来の大規模分析）

### 📊 Application Layer

- 投資判断ダッシュボード（Grafana）
- 経済シグナル自動レポート（週次PDF/Notion連携）
- API連携（TradingView / Slack 通知）

---

## 4️⃣ データモデル（Policy Impact Timeline Schema）

| フィールド | 型 | 説明 |
|---|---|---|
| date | date | ニュース発行日 |
| policy_topic | text | 政策テーマ（例：防衛費増額） |
| company | text | 影響を受ける上場企業名 |
| sector | select | Energy / Defense / Semiconductor / etc |
| impact_score | number | 政策影響度 (0–100) |
| stock_return_3d | number | ニュース後3日間の株価変動率 |
| macro_signal | number | 実体経済の方向（+拡張 / −収縮） |
| lag_correlation | number | 政策→実体への遅延相関係数 |
| classification | select | 一時的 / 構造的下落 / 景気転換前兆 |
| insight | rich text | LLMによる分析コメント |

---

## 5️⃣ モジュール要件

### 🧩 LLM要約・インパクト抽出

- 政策ニュースを JSON 構造化  
- 出力: `policy_topic, expected_industries, potential_beneficiaries, impact_score`  
- 実装: GPT-5 / Codex CLI バッチ（重複排除、URLフィンガープリント）

### 📈 株価連動解析

- yfinance で関連銘柄の 3D/5D リターン取得  
- VAR / XGBoost で政策スコア→価格変動の寄与分解  
- モデル更新の結果を Notion に返送（履歴版管理）

### 🧮 実体経済ラグ検出

- e-Stat / FRED より月次データ取得（PMI/雇用/生産）  
- 政策スコアと各系列の交差相関・ラグ分布を算出  
- ヒートマップ可視化→先行/一致/遅行の分類テーブル生成

### 🧠 リセッション分類AI

- 入力: 株価下落イベント + マクロ系列 + ニュース特徴量  
- 出力: `temporary_correction / structural_recession / sentiment_shock`  
- モデル: LSTM + 経済特徴量エンコーダ（SHAPで説明可能性）

---

## 6️⃣ ビジネス応用（Use-Case）

| 分野 | 活用例 |
|---|---|
| 💰 金融取引 | 政策イベントをリアルタイム検出→関連銘柄のアルゴ指標へ |
| 🏭 経営判断 | 実体経済ラグを把握→設備投資・採用・販売計画の最適化 |
| 📊 レポーティング | 「今週の政策×市場×実体」レポートを自動生成し Notion 投稿 |
| 🧩 RAG連携 | 「最近の防衛政策と株価反応を要約」等の対話検索 |

---

## 7️⃣ 成長戦略（Scalability）

| フェーズ | 内容 |
|---|---|
| Phase 1 | ニュース→株価→政策DB 連携の自動化 |
| Phase 2 | マクロ統合・リセッション判定 |
| Phase 3 | 強化学習による政策対応型アルゴ戦略 |
| Phase 4 | US/EU/ASEAN への拡張 |
| Phase 5 | 企業向け予測APIとして外販（SaaS） |

---

## 8️⃣ 非機能要件（NFR）

- 可用性: バッチは失敗時自動リトライ（3回、指数バックオフ）  
- パフォーマンス: 週次レポート生成 < 10分 / ダッシュボードP95 < 2秒  
- 監視: 取得件数・失敗率・API残クォータ・LLMトークン費用を計測（Grafana）  
- セキュリティ: API鍵は .env + Secrets Manager、PIIは保存しない  
- 監査: 生成物のハッシュ・モデルバージョン・学習データスナップショットを記録

---

## 9️⃣ 検証・受け入れ基準

- バックテスト: イベント後3D/5D の方向一致率が**ナイーブ比**を有意に上回る  
- 一時/構造分類: F1 ≥ 0.6（初期目標）、誤警報率を四半期で低減  
- 再現性: 同一入力に対して同一出力（温度固定、seed管理）

---

## 🔗 根拠（要約）

- 株価は実体経済に先行しやすく、イベント研究で短期窓（1–5D）の効果検出が有効。  
- 政策はセクター別のリターンに即時影響→LLMで正規化し、時系列に統合すれば運用可能。

## Reference

- docs/spec_os/srs.md
