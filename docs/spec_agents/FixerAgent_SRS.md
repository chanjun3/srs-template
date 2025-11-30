# FixerAgent SRS

## 1. Overview & Scope

### 1.1 Purpose

FixerAgent は、CI（GitHub Actions）において lint / format / JSON / link check 等の
静的検査フェーズで Failure が発生した際に自動起動し、

- CI ログ（特に `ci-summary.log`）を解析し、
- 失敗原因を分類（triage）し、
- Global SRS / Syntax Rules / Gate Rules に完全準拠した
  「最小差分（minimal diff）」の修復パッチ案を生成し、

- 自身で一次検証を行ったうえで Pull Request を作成する

自己修復エージェントである。

FixerAgent は **破壊的変更を禁止**される。
すべての処理は Global SRS の不変条件
（CI Syntax Invariants, Failure-Handling Semantics,
 CIFixerAgent Interface Contract, Observability & Critical Fault Definitions）
の範囲内でのみ行われなければならない。

### 1.2 In-scope CI workflows

FixerAgent の対象範囲は、以下を満たす CI workflow_run に限定される。

- GitHub Actions 上で実行された lint / validation 系ワークフロー。
- Global SRS で定義された CI Syntax Invariants を満たす YAML 設定。
- CI 実行結果として、GitHub Actions の artifact `pytest-logs` が生成されているもの。
  （レガシー互換として `srs-ci-logs` を同梱してもよいが、新規パイプラインは `pytest-logs` を必須とする。）
- `pytest-logs` artifact の内容に `pytest_output.txt` が含まれており、FixerAgent が triage・diff 生成の一次ログとして参照できること。

### 1.3 Out-of-scope

FixerAgent は以下には作用しない。

- GitHub Actions に workflow_run が出現していないジョブ
  （Global SRS 上「invalid workflow」として扱われるもの）。

- `pytest-logs` artifact（互換: `srs-ci-logs`）が存在しない、または破損している実行。
- 本番環境でのランタイム障害や外部サービス障害など、
  CI 外のインシデント。

- SRS で明示されていない他リポジトリの CI ワークフロー。
- 手動実行されたローカルスクリプト・ローカルテストの失敗。

これらは FixerAgent の対象外であり、FixerAgent が
自動修復パッチを生成してはならない。

---

## 2. Responsibilities

### 2.1 Core Responsibilities

FixerAgent のコア責務は以下とする。

1. CI Failure の検知とトリガ条件の判定。
1. CI ログからのエラー原因解析と fault classification。
1. Global SRS / Syntax Rules / Gate Rules に準拠した
   最小修復パッチ（minimal diff）の提案。

1. 自己チェック（lint / format / schema 等）による安全性確認。
1. JSON 形式の triage ログの永続化。
1. 自動 PR の作成と ReviewerAgent / 人間へのエスカレーション。

### 2.2 Functional Requirements (FR)

- **FR-1: CI エラー検知**

  - CI Failure（lint / test / build / validation など）が発生した
    `workflow_run` イベントをトリガに起動する。
  - 対象は Global SRS で FixerAgent 対応と定義されたワークフローに限る。

- **FR-2: エラー原因の解析**

  FixerAgent は CI ログおよび `ci-summary.log` から、
  少なくとも以下の種別に分類する。

  - Lint 違反（例：markdownlint, yamllint, flake8 等）
  - 構文エラー（YAML, JSON, Python など）
  - JSON 構文 / Schema 不一致
  - SRS 違反（Global / Local SRS との明示的な矛盾）
  - Gate Rules 違反（非 ASCII, reflow, rewrite 等）
  - 非 ASCII 文字の混入
  - reflow 検知（改行／段落構造の不正変更）
  - diff 量超過（Gate で定義された変更行数上限超過）

- **FR-3: 最小修復パッチの生成（Minimal Patch）**

  - 原則として「壊れた行のみ修正」する。
  - 文意や構造のリライトは禁止する。
  - 既存の段落構造・見出し構造を維持する。
  - コメントや記述の削除は最小限かつエラー解消に必須な場合のみ許可する。

- **FR-4: apply_patch 互換パッチのみ出力**

  - FixerAgent は `apply_patch` 形式で適用可能な diff のみ生成する。
  - 出力は「diff のみ」「context 必須」「deterministic patch」とする。
  - 再実行しても同一入力からは同一 diff を生成しなければならない。

- **FR-5: 自動 PR 作成**

  - パッチ生成に成功し、自己チェックを通過した場合のみ PR を作成する。
  - PR タイトルの形式は `Fix: CI Failure (#<issue_or_run_id>)` とする。
  - PR 説明には 100 文字以内で「原因」と「対応内容」を記載する。

- **FR-6: 自動 PR の自己チェック**

  - FixerAgent は作成した PR が Gate Rules / Syntax Rules に
    準拠しているかを自身で検証しなければならない。
  - 自己チェックに失敗した PR は作成してはならない。

### 2.3 FixerAgent SHALL NOT（禁止事項）

FixerAgent は以下を行ってはならない。

1. Global SRS で定義された CI Syntax Invariants を変更緩和すること。
1. SRS / ポリシー文書の内容をリライトすること
   （誤字修正などの明確なエラー修正を除く）。

1. Gate Rules 違反を含むパッチ案を出力すること。
1. main ブランチに対して直接 merge を実行すること。
1. 対象外の CI workflows（artifact 不在、silent invalidation 等）に対して
   パッチ生成を試みること。

1. 「より良さそう」という主観のみを理由とした改善パッチ
   （仕様変更・大規模リファクタ）を提案すること。

---

## 3. Interfaces & I/O Contracts

### 3.1 Inputs

FixerAgent の入力は次のとおり。

- **workflow_run イベント**

  - GitHub Actions からの `workflow_run` payload。
  なお conclusion が `failure` のもののみを自動修復対象とする。

- **必須 artifact: `pytest-logs`**

  - artifact 名は `pytest-logs` に固定する。Legacy CI で `srs-ci-logs` が必要な場合は
    両方生成してもよいが、FixerAgent Self-Healing Pipeline では `pytest-logs` を最優先で
    探す。
  - artifact 内部に `pytest_output.txt` が含まれていなければならず、最終的に
    `artifacts/pytest_output.txt` として展開できること。
  - artifact が欠如・破損している場合、FixerAgent は `infrastructure_fault` として
    triage ログを出力し、auto-fix を中断する。

- **ログファイル**

  - `pytest_output.txt`（必須）。
  - 任意の補助ログ（`ci-summary.log` など）を参照し、triage 補強データとして記録する。

### 3.2 Outputs

FixerAgent の出力は次のとおり。

- **JSON 形式の triage ログ**

  - 保存先例: `logs/fixer_agent/<run_id>.json`。
  - 少なくとも以下のフィールドを含むこと。
    - `run_id`
    - `workflow_name`
    - `fault_category`
    - `severity`（info / warning / critical）
    - `auto_fix_applied`（true / false）
    - `patch_summary`
    - `srs_references`（参照した SRS セクション）

- **修復パッチ案**

  - `apply_patch` 互換の diff テキスト。
  - 1 つ以上の対象ファイルに対する最小差分。
  - diff 量（追加 + 削除行数）は Gate Rules の上限を超えてはならない。

- **Pull Request**

  - title, body, diff が埋め込まれた PR。
  - ReviewerAgent / 人間がレビュー可能な状態で作成される。

### 3.3 Preconditions

FixerAgent が triage / patch 生成を行う前提条件は以下。

1. `workflow_run` が GitHub Actions 上で確認できること。
2. artifact `pytest-logs` が存在し、`pytest_output.txt` が含まれること。
   （レガシー互換として `srs-ci-logs` + `ci-summary.log` の追加提供は許可するが、省略は不可。）
3. Global SRS で定義された CI Syntax Invariants に
   workflow YAML が違反していないこと
   （Syntax Invariant そのものが壊れている場合は Config fault として扱い、
    FixerAgent は CI YAML を勝手に修正しない）。
4. FixerAgent 自身のバージョンと Global SRS のバージョンが
   サポート範囲内であること（バージョン不整合は Spec/SRS drift として扱う）。

これらの前提条件が満たされない場合、FixerAgent は

**パッチ生成を行わず、triage ログに fault を記録するのみ**とする。

### 3.4 Postconditions

FixerAgent 実行後は以下が保証される。

1. `workflow_run` ごとに 1 つ以上の triage ログ JSON が生成されている。
2. パッチ生成可能なケースでは、
   - diff が Gate Rules / Syntax Rules / Global SRS に準拠している。
    - patch を含む PR が作成されているか、
      生成を断念した理由が triage ログに記録されている。

3. パッチ生成不可能なケース（unknown や infra fault 等）でも、
   必ず fault_category と理由が triage ログに残る。

### 3.5 Technical Requirements (TR)

- **TR-1: CI ログ解析機構**

  - FixerAgent は GitHub Actions API / artifacts からログを取得する。
  - 失敗した Step のログを優先して解析する。
  - エラー種別ごとにパターンマッチ（正規表現 / ルールベース）を行い、
    fault_category 候補を列挙する。

- **TR-2: Diff 生成ロジック**

  - 修正対象ファイルの既存内容を取得し、
    エラー該当行とその前後のみを差分対象とする。
  - 不要な空行の追加や無関係なコードの整形を禁止する。
  - diff 量は Gate Rules で定義される上限行数を超えてはならない。
  - `apply_patch` の形式（hunk header, context 行 等）に完全準拠する。

- **TR-3: Gate Rules との同期**

  - FixerAgent は Global SRS / Gate Rules を参照し、
    非 ASCII, reflow, rewrite 禁止などのルールを常に最新化しておく。
  - Gate 違反になる修復案は即座に破棄し、再生成を試みる。
  - 再生成しても Gate 準拠案が得られない場合、
    auto-fix を断念し triage ログに記録する。

- **TR-4: 安全性チェック前処理**

  - FixerAgent が生成した patch は内部で次の自己監査を実施する。
    - markdownlint / yamllint / JSON validation
    - Python format（black / flake8）
    - 非 ASCII 検知
  - 自己監査に失敗したパッチは PR に使用してはならない。

---

## 4. Behavioral Invariants

### 4.1 行動開始条件

FixerAgent が「行動してよい」条件（MAY act）は次のとおり。

1. `workflow_run` が GitHub Actions 上に存在している。
2. artifact `srs-ci-logs` が正常に取得できる。
3. `ci-summary.log` 内に、少なくとも 1 件のエラー情報が含まれる。
4. fault_category が Source/Content fault または
   CI Configuration fault と判定され、
   かつ auto-fix が許容される範囲である。

上記のうち 1 つでも欠ける場合、
FixerAgent は **パッチ生成 / PR 作成を行ってはならない**。

### 4.2 Guardrails

FixerAgent は次の Guardrails を絶対に破ってはならない。

1. artifact `pytest-logs`（互換として `srs-ci-logs`）が欠如する場合、
   FixerAgent は実行を中断し、Infrastructure fault として記録する。

2. Global SRS 上で定義される「silent invalidation」
   （ログや artifact が出力されないまま lint workflow が終了するケース）は、
   Critical SRS Violation として即時エスカレーションし、
   FixerAgent はパッチ生成を試みない。

3. GitHub Actions 上に workflow_run が存在しない CI 失敗は
   invalid workflow とみなし、FixerAgent の対象外とする。

4. CI Syntax Invariants（YAML インデント, tabs 禁止 など）を壊す
   変更をパッチに含めてはならない。

5. SRS で許可されていないファイル種別・ディレクトリに対して
   パッチを生成してはならない。

6. main ブランチへの直接 push / merge を自動で行ってはならない。

### 4.4 Minimal Triage / Diff / Decision Contract

- FixerAgent SHALL always emit triage logs containing `fault_category`,
  `severity`, `decision`, and `auto_fix_allowed`; absence of any field invalidates
  the run.
- Diff generation SHALL be attempted only when triage reports
  `source_content_fault` and auto-fix is permitted. Other categories SHALL return
  `triage_only` unless the Global SRS explicitly authorizes configuration edits.
- Decisions MUST be one of `auto_fix`, `triage_only`, or `blocked`. `auto_fix`
  requires a patch proposal that passes safety checks and references the exact
  evidence from `pytest_output.txt`.
- Every successful `auto_fix` decision SHALL append a deterministic `diff_hash`
  so ReviewerAgent / PRBuilder can verify patch integrity downstream.

### 4.3 Triage Decision Derivation

FixerAgent の triage 決定は次の流れで導出される。

1. `ci-summary.log` および対象 Step ログからエラー行を抽出。
1. 事前定義されたルールセット（エラーコード / メッセージパターン）により
   各 fault_category のスコアを算出。

1. 最もスコアの高いカテゴリを暫定 classification とし、
   補助情報（対象ファイル拡張子 / 行番号 / YAML or JSON etc.）で微調整。

1. 最終的な `fault_category` と `severity` を決定し、
   triage ログと PR body に反映する。

---

## 5. Risk & Fault Classification

### 5.1 Fault Taxonomy

FixerAgent は CI failure を次の 5 つのカテゴリのいずれかに分類する。

1. **Infrastructure fault**

   - artifact の欠如 / 破損
   - GitHub Actions 側の障害
   - ネットワーク不調によるログ取得失敗 等

2. **CI configuration fault**

   - CI YAML の誤設定（Syntax Invariants との矛盾）
   - artifact 名やパスの変更
   - `continue-on-error` / `if: failure()` 等のガード条件の不整合

3. **Source / Content fault**

   - markdownlint / yamllint / flake8 等の lint 違反
   - JSON 構文エラー / Python format エラー
   - ドキュメント中の明確なタイポ等

4. **Specification / SRS drift**

   - Global / Local SRS の内容と現行リポジトリ構成が乖離している場合
   - SRS 上のパス・命名ルール定義が古く、
     CI との不整合がエラーを生んでいる場合

5. **Unknown**

   - いずれのルールセットにもマッチしないエラー
   - 解析ロジックが未対応の新規エラー形式 等

### 5.2 Behavior per Category

- **Infrastructure fault**

  - FixerAgent は auto-fix を行わない。
  - fault を triage ログに記録し、
    必要に応じて運用者 / Platform チームへエスカレーションする。
  - これらの障害は FixerAgent の失敗としてカウントしてはならない。

- **CI configuration fault**

  - Global SRS の CI Syntax Invariants を守る範囲で、
    CI YAML に対する修正案（最小 diff）を提案してよい。
  - ただし、artifact 名や構造を変更するような修正は
    「SRS 改訂」を前提とするため、
    FixerAgent は auto-fix ではなく
    「SRS 更新が必要」という指摘に留める。
  - 修正案を含む PR は必ず ReviewerAgent / 人間のレビューを必要とする。

- **Source / Content fault**

  - FixerAgent は auto-fix の第一候補とする。
  - minimal diff 原則に従い、エラー行に限定したパッチを生成する。
  - Gate Rules / Syntax Rules をすべて通過した場合のみ PR を作成する。

- **Specification / SRS drift**

  - FixerAgent は仕様そのものを変更してはならない。
  - SRS ファイルへの直接パッチではなく、
    - どの SRS セクションとどの CI 設定が乖離しているか
    - どのような変更方針が必要か
    を triage ログ / PR body に記載する。
  - SRS drift は原則として
    「仕様オーナーへのエスカレーション」として扱う。

- **Unknown**

  - FixerAgent は auto-fix を行わない。
  - triage ログにエラー全文とコンテキストを保存し、
    severity を `critical` または `warning` として記録する。
  - 必要に応じて手動調査の対象とする。

---

## 6. Governance & Operations

### 6.1 Controlled Failure Tests

CI 設定や FixerAgent のロジックに変更が入った場合、
少なくとも次の「制御された失敗ケース」を用いて回帰テストを行う。

1. 代表的な Source / Content fault（markdownlint / JSON エラーなど）。
1. CI configuration fault（意図的に壊した YAML / artifact 設定）。
1. Infrastructure fault（artifact 不在 / 破損を再現したケース）。
1. Spec / SRS drift（意図的に SRS と CI の乖離を起こしたケース）。
1. Unknown fault（解析ロジックでは分類不能なログを入力したケース）。

各ケースについて、

- fault_category が期待どおりに分類されること。
- auto-fix を行うべきケースでのみパッチが生成されること。
- 生成されたパッチが Gate Rules / Syntax Rules に準拠していること。
- Observability & Critical Fault Definitions に反する挙動を
  一切しないこと。

を検証しなければならない。

### 6.2 Postmortem / SRS Feedback Loop

FixerAgent または CI 周りで重大インシデントが発生した場合、
以下のフローで SRS を更新する。

1. 事後分析（postmortem）を作成し、
   - 発生条件
   - root cause
   - 既存 SRS / CI 設定の不足点
   を整理する。

1. 必要であれば Global SRS / FixerAgent SRS のいずれかに
   新たな不変条件やガードレールを追加する。

1. SRS 改訂後、該当ケースを再現する
   Controlled Failure Test を追加し、回帰を防止する。

### 6.3 Human Review / ReviewerAgent Escalation

FixerAgent による auto-fix PR は、以下の条件で
ReviewerAgent または人間レビューが必須となる。

1. 変更行数が Gate Rules のしきい値に近い、またはそれを超えそうな場合。
1. CI configuration fault に対する修正案を含む場合。
1. Spec / SRS drift が関係していると判定された場合。
1. fault_category が `unknown` に近い曖昧なケースで、
   FixerAgent が保守的に auto-fix を提案した場合。

FixerAgent は **決して main ブランチに直接 merge してはならない**。
merge 権限は ReviewerAgent または人間にのみ属する。

### 6.4 Compatibility with Global SRS

FixerAgent は常に Global SRS の不変条件と互換でなければならない。

1. Global SRS 側の CI Syntax Invariants / Interface Contract / Observability 定義に
   変更が入った場合、FixerAgent SRS は追随して更新されること。

2. FixerAgent の動作が Global SRS の定義と矛盾することが判明した場合、
   FixerAgent は当該ケースでの auto-fix を停止し、
   「Spec Update Required」として SRS 改訂を最優先とすること。

3. FixerAgent SRS は Global SRS の下位文書であり、
   矛盾する場合は Global SRS が優先される。

## 7. Self-Healing OS Integration

- FixerAgent は Self-Healing OS チェーンにおいて「上流: Debug AI Agent Automation →
  下流: FixerAgent Self-Healing Pipeline」の接続点を担い、pytest failure artifacts
  から triage/diff/decision を導出する。
- ReviewerAgent および PRBuilderAgent への連携は FixerAgent が生成する triage
  JSON・`diff_hash`・`pytest_output.txt` 参照パスを介して行うものとし、欠損時は次段
  エージェントに制御を渡してはならない。
- Self-Healing OS の健全性評価では、FixerAgent が artifact 欠如時に Critical Fault を
  返し graceful degradation すること、および成功時に auto-fix 決定と PR 生成フローを
  確立することが必須である。
