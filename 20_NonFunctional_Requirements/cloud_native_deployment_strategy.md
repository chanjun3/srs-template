# クラウドネイティブ・デプロイ戦略

## 1. 概要
本ドキュメントは、AIエージェントプロジェクト（例：*policy-tracker-ai*, *job-tracker-ai*）における
クラウドネイティブな開発・デプロイ戦略を定義する。
Codex CLI、GitHub Actions、Docker、Codex SDKを統合した自動化されたDevOpsパイプラインを採用する。

---

## 2. 設計方針
- **マイクロサービス構造**
  各機能を独立したAgent（fetch、summarize、score、notionなど）として分離し、再利用可能にする。
- **ステートレス設計**
  各Agentは状態を保持せず、永続データはNotion DBやFirestoreなど外部で管理する。
- **API駆動設計**
  全ての機能間通信はREST APIまたはGraphQLを通して行う。
- **自動化（Automation）**
  SchedulerAgentとCI/CDにより、定期実行とデプロイを自動化する。
- **可観測性（Observability）**
  実行ログとメトリクスをNotionやCloud Loggingに記録し、パフォーマンスを可視化する。

---

## 3. デプロイフロー概要
1. **Codex CLI**
   ローカル環境でコーディングと初期テストを実施。
2. **GitHubリポジトリ**
   コードをバージョン管理し、リポジトリへプッシュ。
3. **GitHub Actions（CI/CD）**
   自動テスト、Dockerビルド、Cloud Runへのデプロイを実行。
4. **Codex SDK**
   テストログを解析し、自動修正版のPRを生成。
5. **Docker / Cloud Run**
   ステートレスなコンテナとしてクラウド上にデプロイし、スケール可能な実行環境を構築。

---

## 4. CI/CDワークフロー例
```yaml
name: ci-cd-pipeline
on:
  push:
    branches: [ main ]
jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: python -m pytest
      - name: Build Docker Image
        run: docker build -t job-tracker-ai .
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: job-tracker-ai
          image: gcr.io/${{ secrets.PROJECT_ID }}/job-tracker-ai
