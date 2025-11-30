🧾 System Requirements Specification
CI/CD Pipeline – AI-Driven Development Environment

Document ID: SRS-CICD-001
Author: jun1_
Date: (更新日を記入)
Version: 1.0

## 1. 概要（Overview）

本ドキュメントは、AIエージェント（Codex CLI）を用いた開発環境における
CI/CDパイプラインおよび品質保証プロセスの要件定義を示す。
目的は、**「壊れない品質」と「開発速度の両立」**を実現することである。

## 2. システム目的（Purpose）

コードと環境の両面で再現性を保証する。

CodexによるAI駆動型開発を自動テスト・自動デプロイに統合。

GitHub Actionsを中心に、自動化・観測・修復が循環する仕組みを確立。

## 3. パイプライン全体構成（Architecture）

構成要素
要素    役割
GitHub Actions    CI/CDの中核。Lint/Test/Build/Deployを自動化。
Docker    環境の一貫性を担保。開発・テスト・本番を同一コンテナで実行。
Vercel / Cloud Run    デプロイ先環境。フロントエンドとAPIの自動デプロイ。
Notion DB    テスト結果・ビルドログ・メトリクスを記録し、知識資産化。
Codex CLI    各フェーズのコード生成・修正・統合を担う開発AI。

## 4. CIフェーズ（Continuous Integration）

### 4.1 実行トリガ

pull_request → Lint / Unit Test

push to main → Integration Test / Build / Deploy

### 4.2 Lint & Test ワークフロー

name: Lint & Test (PR)
on:
  pull_request:
    branches: [ main ]

jobs:
  lint_test:
    uses: ./.github/workflows/reusable-lint-test.yml

### 4.3 テスト基準

種類    内容    実行タイミング
Lint    コーディング規約違反チェック    PR時
Unit Test    機能単体の正当性    PR時
Integration Test    API・DB連携動作    main merge時
E2E Test    CI完了後に自動または手動    ステージング環境

## 5. CDフェーズ（Continuous Deployment）

### 5.1 Vercel 自動デプロイ

vercel pull --yes --environment=production --token=
vercel build --prod --token=
vercel deploy --prebuilt --prod --token=

### 5.2 Cloud Run 自動デプロイ

gcloud run deploy policy-tracker-ai \
  --image "" \
  --region "" \
  --platform managed \
  --allow-unauthenticated

### 5.3 Notionレポート自動送信

デプロイ完了後、Notion APIに結果をPOST

プロパティ：Title, Commit, Status, URL, BuildTime

## 6. Dockerによる環境統一

### 6.1 目的

「ローカル・CI・本番」すべての環境差を排除。

再現性と可搬性を確保することで“壊れない品質”を保証。

### 6.2 設計要件

要件    内容
ベースイメージ    node:20-alpine / python:3.11-slim
ビルド構成    multi-stage buildで軽量化
健康監視    HEALTHCHECK CMD curl -f <http://localhost:8080/health>
セキュリティ    OIDC認証、最小権限IAM運用
キャッシュ最適化    npm/pip cacheを利用して高速化

## 7. Codex開発プロセス統合要件

### 7.1 開発方針

Codex CLI（Chatモード）を活用し、SRS（要件定義）を分野ごとに分割してAIに指示。

開発初期：タスク単位で分野別プロンプトを投げる。

統合段階：6分野の要件をまとめて投げ、整合性を最適化。

### 7.2 指示テンプレート

# Context

Project: {project_name}
Domain: {SRS Domain}
File: {target_file}

# Reference

Refer to: {SRS_File.md} section "{section_title}"

# Task

{具体的な指示内容}

## 7.3 Codex統合フロー

1. SRS分野別タスク → コード生成
1. GitHub Actions → 自動テスト
1. Codexへ統合指示 → 依存関係整合化
1. Notionへ成果保存 → RAG連携

## 8. 品質保証要件（Quality Assurance）

要素    要件内容
自動テスト    全フェーズで自動実行（PR→Deploy）
失敗検知    GitHub Actionsで失敗をSlack/Notion通知
メトリクス    Fetch件数・失敗率・トークンコストをCloudWatch/Grafanaで可視化
再現性    Dockerイメージで全テストを再実行可能
監査性    コミットID × イメージID × レポートID の対応を保持

## 9. 開発・運用ルール

各プロジェクトは独立した project_root 構成で管理。

System Requirements Specification Template を共通テンプレートとして利用。

CI/CD設定、Notion同期、Dockerfileはテンプレートから再利用可能。

## 10. 改訂履歴

バージョン    日付    内容    作成者
1.0    (日付)    初版作成    jun1_

🎯 Summary

このSRSは「Codex × GitHub Actions × Docker」で実現する
AI駆動の完全自動化パイプラインの設計思想を定義する。
目的は「壊れない品質 × 自己進化する開発環境」。
これをベースにすれば、すべての新プロジェクトで
高速・安定・再現可能な開発サイクルを再現できる。 🚀

💾 保存場所：
C:\Users\jun1_\Desktop\System Requirements Specification Template\50_Quality_Assurance\CI_CD_Pipeline_SRS.md

## Reference Links

- docs/spec_os/srs.md
## 11. Self-Healing CI/CD Requirements

### 11.1 Silent Invalidation Detection & Prevention

- すべての lint/test workflows は `if: always()` を活用してログ生成と artifact アップロードを保証し、静かな失敗（silent invalidation）を防止しなければならない。
- GitHub Actions の `workflow_run` イベントに現れない実行は無効と見なし、Failure の根本原因を再発防止記録に残さなければならない。
- FixerAgent 起動ワークフローは、上流の `Debug AI Agent Automation` 実行から `conclusion` フィールドを継承し、`failure` 以外では自動修復を試みてはならない。

### 11.2 YAML Syntax Invariants

- すべての CI YAML は 2 スペースインデントを必須とし、タブおよび混在インデントを禁止する。
- `run: |` ブロックの内部インデントは `run` キー基準からの相対スペースを固定し、途中で変化させてはならない。
- インデント違反は `CI configuration fault` と定義し、FixerAgent および ReviewerAgent は検出時に triage ログへ Critical Fault として記録する。

### 11.3 Artifact Generation Requirements

- `Debug AI Agent Automation` は必ず `pytest_output.txt` を生成し、artifact 名 `pytest-logs` としてアップロードしなければならない。
- Artifact のアップロードステップは `if: always()` を伴い、pytest の成功・失敗に関わらず実行されなければならない。
- FixerAgent Self-Healing Pipeline は `pytest-logs` artifact の存在を前提条件とし、不足時には auto-fix を試みず Critical Fault を報告する。

### 11.4 Failure Injection Specification

- OS 的自己修復検証のため、意図的にテストや lint を失敗させる Failure Injection を許可し、FixerAgent のレジリエンスを定期検証する。
- Failure Injection 実施時は、対象コミット・再現手順・期待される triage 結果を記録し、SRS 更新サイクルにフィードバックしなければならない。

### 11.5 Critical Fault Handling

- Artifact が欠如・破損している場合、FixerAgent は Infrastructure fault として失敗を記録し、OS 全体を停止させることなく graceful degradation で終了しなければならない。
- Critical Fault の発生は Assurance チームにエスカレーションし、再発防止策を CI/CD SRS と Global SRS に反映させる。
