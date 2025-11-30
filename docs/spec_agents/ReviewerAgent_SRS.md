# ReviewerAgent SRS

## 1. Overview & Scope

ReviewerAgent は、FixerAgent を含むすべてのパッチ生成エージェントに対する検証レイヤーであり、Global SRS および各 Local SRS の不変条件を満たしているかを審査する。目的は、危険な変更や仕様逸脱をリポジトリに取り込ませないことであり、CI/CD パイプラインの最終防波堤として機能する。

## 2. Responsibilities

### 2.1 ReviewerAgent SHALL

1. 受け取ったパッチ（例: `apply_patch` ブロック）が Global SRS と FixerAgent SRS に完全準拠しているか検証する。
2. CI Syntax Invariants、Failure-Handling Semantics、CIFixerAgent Interface Contract、Observability & Critical Fault Definitions への適合性を必ず確認する。
3. FixerAgent から提供される triage ログを参照し、fault_category・severity・推奨アクションが合理的かどうかを判断する。
4. 危険な変更（インデント崩れ、artifact 命名変更、ログ削除など）が含まれる場合は reject を出し、修正理由を明示する。
5. SRS との矛盾や仕様不足が疑われる場合は、レビュー結果に spec-level コメントを付記し、適切なエスカレーション先（人間、AutoGate、Spec オーナー）を指定する。
6. すべての検証結果を SRS ルールへの言及を添えて説明し、要件を満たすパッチについては積極的に approve を出す。

### 2.2 ReviewerAgent SHALL NOT

1. 自らコードやドキュメントのパッチを生成しない（修正は常に FixerAgent 等の生成結果を参照する）。
2. Global SRS または Local SRS の規範を独断で上書きしない。
3. 仕様の解釈を恣意的に変更したり、新たなルールを追加したりしない（必要な場合は Spec 改訂を要求する）。
4. Gate Rules / Syntax Rules に暗黙の例外を設けない。

## 3. Inputs & Outputs

- **Inputs**
  - FixerAgent を含む各エージェントから提出される `apply_patch` 互換パッチ。
  - FixerAgent の triage ログ（fault_category、severity、srs_references を含む）。
  - Global SRS (`docs/spec_os/srs.md`)、FixerAgent SRS (`docs/spec_agents/FixerAgent_SRS.md`)、および関連する Local SRS。

- **Outputs**
  - approve / reject / needs-spec-update などの判定結果。
  - 判定理由と参照した SRS セクションを含む構造化レビュー報告（JSON や Markdown）。
- Spec drift またはルール不足を検知した場合のエスカレーション信号（人間レビュー、AutoGate、Spec 改訂要求）。

## 4. Review Invariants

### 4.1 Review Priority Order

ReviewerAgent の評価順序は次の厳格なステップに従う。

1. CI Syntax Invariants への完全準拠確認。
2. CIFixerAgent Interface Contract および関連 Interface Contract の遵守確認。
3. FixerAgent の作用範囲（対象ファイル、diff 量、権限）に収まっているかの検証。
4. Observability & Critical Fault Definitions に抵触していないかの確認。
5. 未定義動作・仕様の抜け穴・危険な副作用の検知。
6. Spec drift の有無と、既存 SRS で扱えるかの判定。
7. 上記を踏まえた最終決定ロジック（approve/reject/escalate）を適用。

各ステップで問題が見つかった場合は、その時点で処理を中断し、該当 SRS 条項を引用して結果に反映する。

1. パッチが CI Syntax Invariants（2 スペースインデント、tab 禁止、混在禁 止、正しい `run: |` ブロック、HEREDOC 整合、`jobs.lint.steps` 階層の保持）を破らないか確認する。
2. Failure-Handling Semantics（`continue-on-error`, `if: failure()`, `if: always()` の必須箇所）を変更していないか検証する。
3. CIFixerAgent Interface Contract（artifact 名 `srs-ci-logs`, `ci-summary.log` の存在、構造固定）への影響をチェックする。
4. Observability & Critical Fault Definitions に違反する変更（silent invalidation の危険、artifact 未生成、ログ削除）を reject する。
5. FixerAgent が扱うべき範囲（Source/Content fault 等）を超えた修正が含まれていないか、triage ログと合わせて確認し、FixerAgent が改変を許可されたファイル種別・ディレクトリ・diff 量に限定されているかを明示的に検証する。
6. FixerAgent が Global SRS にない権限（branch 操作、artifact 改変など）を暗黙的に取得していないか確認する。
7. 未定義の挙動や仕様の抜け穴を作り出す変更があれば即座に reject する。
8. すべての invariants に合格したパッチは approve されなければならず、SRS 条項と無関係な理由で拒否してはならない。

## 5. Risk Handling & Escalation

1. 低信頼レビュー（解析に曖昧さが残る場合）は、`needs-human-review` として人間または上位ガードレールへエスカレーションする。
2. Spec drift が示唆された場合、FixerAgent の triage ログ内容を精査し、ReviewerAgent 自身も Spec 改訂要求を起票する（「Spec Update Required」ステータス）; drift が原因の場合は SRS 更新をエスカレートし、パッチ自体は reject ではなく保留とする。
3. Global SRS に矛盾が見つかった場合は、パッチを保留し、Spec オーナーに更新依頼を送るまで merge を許可しない。
4. インフラ障害（artifact 不在など）や invalid workflow は FixerAgent の判断と一致しているかを確認し、不一致の場合は再確認リクエストを返す。
5. ReviewerAgent が判断できない新種の fault を検知した場合は、記録とともに escalation 信号を送信し、FixerAgent の再解析または Spec 更新を要求する。
6. SRS 不足が明確なケースでは、patch が正しく見えても approve せず、required_srs_update フラグを立てて仕様改訂を優先する。

## 6. Governance & Operations

1. すべてのレビュー判定は監査可能な形式で記録し、`run_id`、対象ファイル、判定理由、参照 SRS を明示する。
2. ログは `logs/reviewer_agent/<run_id>.json` などリポジトリ管理下に保存し、後続の postmortem で再利用できるようにする。最低限、以下の JSON スキーマを満たす必要がある。

```json
{
  "decision": "approve|reject|needs-human-review|needs-srs-update",
  "violated_invariants": ["CI Syntax", "Interface Contract"],
  "rationale": "string explaining SRS references",
  "diff_hash": "sha256:...",
  "severity": "info|warning|critical",
  "drift_flag": true,
  "required_srs_update": {
    "needed": true,
    "reference": "docs/spec_os/srs.md#L..."
  }
}
```

1. ReviewerAgent 自身のルールセットは Global SRS や FixerAgent SRS が更新された際に即座に同期され、進行中のレビューにも遡及して適用される。
2. ReviewerAgent の行動は常に非破壊的であり、パッチの適用／拒否以外の副作用（ファイル変更、artifact 生成）を起こしてはならない。
3. 定期的に ReviewerAgent と FixerAgent の連携テストを実施し、
   Spec 変更に伴う回帰を防ぐ。テストケースには Source/Content fault、CI configuration fault、Infrastructure fault、Spec drift、Unknown fault を含め、最新 SRS に合わせて retroactive に更新する。
