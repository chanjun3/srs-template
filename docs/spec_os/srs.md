# System Requirements Specification (Global SRS)

1. Overview
2. System Architecture
3. Behavioral Rules
4. Syntax Rules
   4.1 Markdown Rules
      - 見出しは 1 レベルずつ昇格 (MD001)
      - 見出し前後は空行1つ (MD022)
      - 番号リストは常に "1." (MD029)
      - 箇条書き前後に空行 (MD032)
      - コードフェンス前後に空行 (MD031)
      - 160文字以内 (MD013)
      - 裸URL禁止 (MD034)
      - タブ禁止 (MD010)
      - 空行は最大1つ (MD012)
      - EOFは1改行 (MD047)

   4.2 YAML Rules
      - インデントは2スペース
      - タブ禁止
      - 重複キー禁止

   4.3 JSON Rules
      - trailing comma禁止
      - strict JSONのみ

   4.4 Python Rules
      - black準拠
      - flake8違反禁止
5. Functional Requirements (Links Only)
   - PlannerAgent: docs/requirements/functional/planner/Local_SRS.md
   - CoderAgent: docs/requirements/functional/coder/Local_SRS.md
   - CriticAgent: docs/requirements/functional/critic/Local_SRS.md
   - ReviewerAgent: docs/requirements/functional/reviewer/Local_SRS.md
   - OrchestratorAgent: docs/requirements/functional/orchestrator/Local_SRS.md
   - ResearchAgent: docs/requirements/functional/research/Local_SRS.md
6. Non-functional Requirements (Links Only)
7. Data Requirements (Links Only)
8. Integration Requirements (Links Only)
9. Assurance / CI/CD Requirements (Links Only)
10. Glossary
