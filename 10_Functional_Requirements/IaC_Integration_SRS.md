# 🧭 System Requirements Specification (SRS)
## Cloud-Native基盤へのIaC化（Terraform + GitHub Actions）

---

### 1. 概要
本ドキュメントは、Terraform と GitHub Actions を用いた Cloud-Native 環境へのデプロイ自動化に関する要件定義を示す。  
目的は、chanjun3プロジェクト群（Policy-Tracker-AI、MacroSignal、AI Website Studioなど）における**インフラ環境の自動構築・管理・再現性向上**である。

---

### 2. 背景と目的
現行の開発体制では、複数のAIエージェントがそれぞれ別環境上で稼働しており、環境構築手順が属人的かつ再現性に乏しい。  
IaC化により、インフラ構成をコードで定義し、CI/CDとの統合によって、**迅速・安全・一貫したデプロイ**を実現する。

#### 目的の要約
- クラウド環境構成の自動化
- デプロイ作業のヒューマンエラー削減
- 環境の再現性・スケーラビリティ確保
- コードと環境構成の統一管理

---

### 3. システム構成概要

#### 3.1 全体アーキテクチャ
GitHub Repository
├── .github/workflows/deploy.yaml # CI/CDワークフロー定義
├── terraform/
│ ├── main.tf # インフラリソース定義
│ ├── variables.tf # パラメータ管理
│ └── outputs.tf # 出力値定義
└── secrets/ # GitHub Secrets (認証情報)

yaml
コードをコピーする

#### 3.2 環境要素
| 要素 | 内容 |
|------|------|
| **Terraform** | クラウドリソース構成の宣言的定義 |
| **GitHub Actions** | CI/CDによる自動デプロイ |
| **GitHub Secrets** | APIキー・クレデンシャル管理 |
| **Cloud Run / Supabase / GCS** | デプロイ対象環境 |

---

### 4. 機能要件

| ID | 要件名 | 説明 |
|----|--------|------|
| FR-01 | IaC構築 | Terraformを利用してGCP/AWS/Azure環境をコードで定義 |
| FR-02 | 自動デプロイ | GitHub Actionsにより自動plan/applyを実行 |
| FR-03 | 環境再現 | 同一構成を別環境へ容易に再構築可能 |
| FR-04 | Secrets管理 | APIキーや環境変数をGitHub Secretsに安全に格納 |
| FR-05 | ステート管理 | Terraform stateをGCS/S3に保存・ロック制御を実施 |
| FR-06 | 変更レビュー | PR作成時に`terraform plan`を自動実行し差分確認 |

---

### 5. 非機能要件

| ID | カテゴリ | 要件 |
|----|-----------|------|
| NFR-01 | セキュリティ | SecretsとIAMロールにより最小権限原則を徹底 |
| NFR-02 | 可用性 | GitHub Actionsのself-hosted runner対応を検討 |
| NFR-03 | スケーラビリティ | モジュール設計により複数環境（dev/prod）を切替可能 |
| NFR-04 | 運用性 | `terraform plan`と`apply`をCI/CDパイプラインで可視化 |
| NFR-05 | 拡張性 | ArgoCDやEventBridgeとの統合によるGitOps拡張性 |

---

### 6. 運用フロー

1. 開発者が`terraform/*.tf`を変更  
2. Pull Request 作成 → GitHub Actions が `terraform plan` 実行  
3. 差分レビュー後、`main` へマージ  
4. 自動で `terraform apply` 実行 → クラウドへ反映  
5. 成果を Notion DB または Slack 通知へ自動連携  

---

### 7. 期待効果

| 観点 | 効果 |
|------|------|
| 再現性 | 同一構成を迅速に展開可能 |
| 開発効率 | 手動操作削減により30〜60分短縮 |
| セキュリティ | Secrets一元管理・監査ログ化 |
| 信頼性 | すべての構成変更をコードベースで追跡可能 |
| 自律性 | 将来的にAIエージェントがインフラ調整を自己学習可能 |

---

### 8. 今後の拡張案（フェーズ2以降）
| フェーズ | 概要 |
|-----------|------|
| IaC v1 | Terraform + GitHub Actionsで自動構成化 |
| IaC v2 | ArgoCDによるGitOps連携 |
| IaC v3 | EventBridge + Serverlessによる自己修復構成 |
| IaC v4 | AIエージェントによる状態最適化（ACES統合） |

---

### 9. リスクと対策
| リスク | 対策 |
|---------|------|
| Terraform State競合 | Locking機構（DynamoDB/GCS）を実装 |
| Secrets漏洩 | GitHub Secretsアクセス制御を設定 |
| 誤apply | `plan`結果レビューを必須化 |
| 権限過多 | ServiceAccount権限を最小化 |

---

### 10. 承認とバージョン管理
| 項目 | 値 |
|------|----|
| 作成者 | chanjun3 |
| 作成日 | $(Get-Date -Format "yyyy-MM-dd HH:mm:ss") |
| バージョン | 1.0.0 |
| 保管場所 | System Requirements Specification Template / 10_Functional_Requirements |
| 関連ドキュメント | IaC_Integration_Report.md, deploy.yaml, main.tf |

---
