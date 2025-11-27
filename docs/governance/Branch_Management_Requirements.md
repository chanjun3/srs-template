# AI協調開発ブランチ運用 標準要件定義書（System-Wide Version）

## 1. 目的

本ドキュメントは、AIエージェント（Codex / GPT）と人間開発者が協調して開発を行う際の  
ブランチ運用基準を定義する。  
自動修正やCI/CDを安全かつ再現性高く行うための標準プロセスを明文化する。

---

## 2. 運用モデル概要

開発者（dev-main） ← CodexCLIで設計・開発
↓ push
GitHub Actions（CI/CD）
↓
pytestテスト → エラー → Codex SDKによる自動修正
↓
dev-auto-fixブランチへpush
↓
自動PR → main（責任者がレビュー後マージ）

yaml
コードをコピーする

---

## 3. 標準ブランチ構造

| ブランチ | 役割 | 操作者 | トリガー | 備考 |
|-----------|------|----------|----------|------|
| main | 安定版／承認済みコード | 責任者 | PR承認 | 保護ブランチ（push禁止） |
| dev-main | 開発・設計用 | 開発者 or CodexCLI | push | テスト・ビルドトリガー |
| dev-auto-fix | 自動修正結果保存 | GitHub Actions＋Codex SDK | failure() | 自動PR生成 |

---

## 4. GitHub Actions運用要件

| 項目 | 内容 |
|------|------|
| ワークフロー名 | Codex Auto-Fix Workflow |
| トリガー | push to dev-main |
| 成功条件 | pytest成功／Codex修正完了 |
| 失敗時動作 | Codex SDKによる修正＆PR生成 |
| 使用トークン | AI_AGENT_API_KEY, GITHUB_TOKEN |
| 環境 | ubuntu-latest / Python 3.12 以上 |

---

## 5. セキュリティ／権限要件

- mainブランチ：直接push禁止（保護設定必須）  
- Codex SDKはAI_AGENT_API_KEY（GitHub Secrets）を使用  
- 自動修正の差分はPull Request経由で可視化  
- 全修正履歴はGitHub PRとNotionに自動記録  

---

## 6. 拡張運用

- デプロイ自動化：mainマージ後にCloud Run / Vercelへ展開  
- 品質メトリクス：Codex修正頻度を分析し品質スコアを算出  
- 知識化：修正ログをNotion DBに同期（RAG対応）

---

## 7. バージョン管理

| バージョン | 改訂日 | 改訂内容 |
|-------------|----------|-----------|
| 1.0 | $(Get-Date -Format "yyyy-MM-dd") | 初版：標準ブランチ運用要件定義化 |

---

作成者: chanjun3  

## Reference

- docs/spec_os/srs.md
