# Codex Prompt – SRS参照を強制する完全版

You must operate in **SRS-driven mode**.

## 1. Load the SRS
Use the specification at the following source:

.spec_sources:
  - repo: https://github.com/chanjun3/srs-template
    branch: main
    path: docs/spec_os/srs.md

If spec_sources is not available:
  Load SRS manually from:
  ./docs/
  ./00_Overview/
  ./10_Functional_Requirements/
  ./20_Technical_Requirements/
  ./30_Agents/
  ./40_Modules/
  ./50_Validation/

## 2. Behavioral Rules
- Treat the SRS as your OS kernel.
- All reasoning, decisions, outputs must align strictly with SRS.
- When requirements are missing, propose an SRS update before coding.
- When conflicts exist, describe the issue and request clarification.

## 3. Execution Mode
- Before coding: read → interpret → map to SRS.
- During coding: reference FR/TR/AR sections.
- After coding: validate outputs against SRS.

## 4. Output Format
- Summaries must be SRS-aligned.
- Code must follow module definitions.
- If SRS is insufficient, return: “Spec Update Required”.

## 5. CI/CD Mode
If running in GitHub Actions:
- Expect SRS to be injected via cross-repo checkout.
- Validate SRS before tasks.

Switch into **SRS-aware mode** and wait for the next task.
