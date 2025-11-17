# 🧩 情報収集AIシステム 要件定義書  
**（Standard Collector-Agent Framework Requirements）**

---

## 1. 概要
本システムは、異なる構造・形式を持つWeb情報（求人・政策・市場情報など）を自動収集し、
統一スキーマへ正規化（Normalization）して蓄積・分析するAIシステムである。  
「サイトごとに最適な収集方法が異なる」という原理を基礎とし、
**Collector → Normalizer → Analyzer** の3層構造によって拡張性・再利用性・自動化を確保する。

---

## 2. システム目的
1. 各種Webサイト（HTML、API、RSS等）からの情報収集を自動化  
2. 異構造データを共通フォーマットに変換（構造化変換）  
3. Notion DBやCSVなどに格納し、GPTを活用した要約・分類・スコアリングを実行  
4. 政策・求人・市場トレンドなど横断的な分析を可能にする基盤を提供

---

## 3. システム構成（3レイヤーモデル）

### 3.1 🔍 Collector Layer（データ取得）
- **目的**：情報ソース（Web・API・RSS）からデータを取得  
- **手法**
  - HTMLスクレイピング：`requests`, `BeautifulSoup`
  - API取得：`requests.get(token付)`
  - RSS取得：`feedparser`
  - 動的サイト対応：`Selenium` または `fetch`リクエスト解析  

| サイト種別 | 代表例 | 最適取得方法 |
|-------------|---------|---------------|
| HTML静的（SSR） | FLEXY, Indeed | requests + BeautifulSoup |
| SPA型（React/Vue） | デジタル庁, Findy | Selenium / fetch解析 |
| RSS公開型 | PR Times, 官報 | feedparser |
| REST API | GitHub Jobs, Indeed API | requests + token |
| GraphQL | Findy, Wantedly | GraphQLクエリ送信 |
| PDF/テキスト型 | 調達公告, 契約書 | pdfminer / regex |

---

### 3.2 🧠 Normalization Layer（構造化変換）
- **目的**：ソースごとに異なる構造を統一スキーマへ変換  
- **機能**
  - HTML/JSON/XMLの正規化
  - スキーママッピング：`normalize_jobs.py`
  - ネスト解除（flatten）
  - 欠損補完・型変換

#### 出力スキーマ例

```json
{
  "source": "FLEXY",
  "title": "AIエンジニア（リモート可）",
  "company": "TechCorp株式会社",
  "job_type": "業務委託",
  "working_days": "週2-3日",
  "salary": "月60〜80万円",
  "location": "リモート",
  "skills": ["Python", "GPT", "自動化"],
  "link": "https://flxy.jp/jobs/12345",
  "published_at": "2025-11-05T09:00:00Z"
}
3.3 📊 Storage & Analysis Layer（蓄積・分析）
目的：統一データを保存・要約・分析

保存形式

Notion DB / SQLite / S3 / CSV

分析機能（GPT活用）

処理    GPTの役割
カテゴリ分類    「AI」「DX」「営業」などを自動タグ化
要約    案件説明を200文字以内に要約
スコアリング    報酬・スキル一致率・急募度を算出
トレンド分析    「今週多いスキル」「報酬上昇傾向」を抽出

4. 実装構成例（ファイル構造）
レイヤー    ファイル名    機能
Collector    fetch_flexy.py, fetch_findy.py, fetch_digital_agency.py    各サイト固有の取得
Normalizer    normalize_jobs.py    共通スキーマへ変換
Storage    upload_notion.py    Notion DBまたはCSV出力
Analyzer    classify_jobs.py, trend_summary.py    GPT分類・要約・スコアリング
Scheduler    run_daily.ps1, .github/workflows/collector.yml    定期自動収集実行

5. 処理フロー（シーケンス概要）
mermaid
コードをコピーする
graph TD
A[Schedule Trigger] --> B[Collector Layer]
B --> C[Raw Data (HTML/JSON/RSS)]
C --> D[Normalization Layer]
D --> E[Unified JSON Schema]
E --> F[Storage (Notion/CSV)]
F --> G[Analyzer (GPT Summary, Scoring)]
G --> H[Reports / Dashboards]
6. 非機能要件
項目    要件内容
自動化    GitHub Actions / PowerShellによるスケジューリング
セキュリティ    APIキー・トークンは.env管理
拡張性    新規サイト追加は Collector/Normalizer モジュール追加で対応
可観測性    ログ出力・例外ハンドリング・通知連携（Slack/Notion）
メンテナンス性    ソース構造変更時の修正箇所を限定化（レイヤー分離）

7. 今後の拡張計画
Multi-Agent化（CollectorAgent / NormalizerAgent / AnalyzerAgent）

RSS・APIの統合監視機能

GPT要約精度チューニング（システムプロンプト調整）

Notionダッシュボード連携

政策・求人・金融データの共通スキーマ運用（Policy-Tracker-AI, JobWatcher-AI 連携）

8. 根拠・考察
Normalization Layer が抽象化の鍵であり、
GPTを組み込むことで単なる情報収集ではなく
「意味理解」と「優先順位付け」を自動化できる。
Collector-Agent Framework化することで、ニュース・求人・政策・マーケット分析を同一基盤で処理可能。
