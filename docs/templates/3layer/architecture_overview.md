# AIエージェント標準: 3層アーキテクチャ概要

## 1. Purpose
標準エージェントの採用に必要となるデータ / ワークロード基盤を
「Supabase（構造化 DB）× Qdrant/Weaviate（ベクトル DB）× Notion（UI 管理）」で定義し、
Collector / Normalizer / Analyzer が継続稼働できる参照モデルを提示する。

## 2. Background
Codex SDK / Agent SDK のログや状態管理は段階関数的に連動するが、
Notion 一体型だけでは保存粒度・権限・構造の不整合でスケールできない。
そのため取得（Collector）、整形（Normalizer）、活用（Storage & Analysis）を分離し、
3 層構成で責務を固定化する必要がある。

## 3. Layered Structure

### 3.1 Collector Layer（データ取得）
- **役割**: Web / API / RSS / PDF など各ソースからのデータ収集。
- **主要ツール**: `requests`, `BeautifulSoup`, `feedparser`, `Selenium` など。
- **サイト種別と取得方法**

| サイト種別 | 例 | 収集方法 |
| --- | --- | --- |
| HTML（SSR） | FLEXY, Indeed | requests + BeautifulSoup |
| SPA（React/Vue） | デジタル庁, Findy | Selenium / fetch |
| RSS | PR Times 等 | feedparser |
| REST API | GitHub Jobs | requests + token |
| GraphQL | Wantedly | GraphQL クエリ |
| PDF / テキスト | 官報 等 | pdfminer / regex |

### 3.2 Normalization Layer（フォーマット統一）
- **役割**: 収集データを共通 JSON スキーマへ変換。
- **実装**: HTML/JSON/XML クリーニング、`normalize_jobs.py` によるスキーマ適用、テキスト正規化。
- **出力例**

```json
{
  "source": "FLEXY",
  "title": "AIエンジニア（在宅可）",
  "company": "TechCorp株式会社",
  "job_type": "業務委託",
  "working_days": "週2-3日",
  "salary": "月60〜80万円",
  "location": "リモート",
  "skills": ["Python", "GPT", "検索"],
  "link": "https://flxy.jp/jobs/12345",
  "published_at": "2025-11-05T09:00:00Z"
}
```

### 3.3 Storage & Analysis Layer（蓄積・活用）
- **Supabase**: 実行ログ・進捗・メタデータの永続化。
- **Qdrant / Weaviate**: Embedding 検索と知識再利用。
- **Notion**: 人の閲覧 UI（SRS、データ辞書、タスク状態等）。
- **分析**: Unified JSON Schema → Notion/CSV/SQLite/S3 へ格納 → GPT で要約/スコアリング。

## 4. Architecture Diagram
Agents → Supabase（Logs）→ Qdrant/Weaviate（Search）→ Notion（Knowledge UI）

```mermaid
graph TD
  A[Schedule Trigger] --> B[Collector Layer]
  B --> C[Raw Data (HTML/JSON/RSS)]
  C --> D[Normalization Layer]
  D --> E[Unified JSON Schema]
  E --> F[Storage (Supabase/Notion)]
  F --> G[Analyzer (GPT Summary, Scoring)]
  G --> H[Reports / Dashboards]
```

## 5. Scope
本書はアーキテクチャ概要を対象とし、詳細要件は各プロダクト SRS に委譲する。
Collector/Normalizer/Analyzer のコード資産や運用ガイドのシングルソースとして機能させる。

## 6. Operational Assets

| レイヤー | ファイル | 説明 |
| --- | --- | --- |
| Collector | `fetch_flexy.py`, `fetch_findy.py`, `fetch_digital_agency.py` | 各サイトの取得スクリプト |
| Normalizer | `normalize_jobs.py` | 取得データを共通スキーマへ整形 |
| Storage | `upload_notion.py` | Notion / CSV への格納処理 |
| Analyzer | `classify_jobs.py`, `trend_summary.py` | GPT での要約・スコアリング |
| Scheduler | `run_daily.ps1`, `.github/workflows/collector.yml` | 定期実行トリガー |

## 7. 期待成果と運用
- GitHub Actions / PowerShell でのスケジューリング。
- API キーやトークンは `.env` で集中管理。
- 新規サイト追加時は Collector / Normalizer モジュールを追加・即テスト。
- Slack / Notion でエラー通知・完了報告を実施。

## 8. リスクと緩和
- Normalization Layer がボトルネック化する恐れ → スキーマテストを自動化。
- GPT 依存の分析は説明責任を伴う → ルールベース分類とのハイブリッド運用。
- Collector-Agent Framework 拡張性を確保し、業務要件に応じたエージェント追加を容易にする。
