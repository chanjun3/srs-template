🧾 System Requirements Specification  
Data Utilization & Learning Policy  

Document ID: SRS-DATA-001  
Author: jun1_  
Date: (更新日を記入)  
Version: 1.0  

## 1. 概要

本ドキュメントは、データ収集・要約・保存・AI学習利用の各段階における
法的・技術的ガイドラインを定義する。

## 2. データ収集

- SRRおよびX（旧Twitter）経由のデータ収集は、プラットフォーム規約に従い実施。
- 収集データには `license` メタ情報を付与。

## 3. データ変換

- LLMによる要約生成を実施。
- 要約結果は新規著作物として扱い、学習利用を許可。

## 4. 保存期間

| データ種別 | 保存期間 | 処理方針 |
|-------------|-----------|----------|
| RAWデータ | 30日 | 自動削除 |
| 要約データ | 無期限 | 学習可 |
| ログ | 7日 | 自動削除 |

## 5. 法的準拠

- 個人情報保護法 / GDPRに基づきデータ最小化原則を遵守。
- モデル学習禁止条項（X Developer Agreement）を考慮。

## 6. 実装要件

- `safe_for_training` フィールドで利用可否を制御。
- `storage_agent.py` にTTL（削除期限）を設定。

## 7. 運用方針

- 定期的にポリシー更新。
- Data Governance Dashboardで可視化。

## 8. 改訂履歴

| Version | Date | Description |
|----------|------|--------------|
| 1.0 | (日付) | 初版作成 |

## Reference

- docs/spec_os/srs.md
