# Config artefacts

YAML payloads referenced by SRS documents and case studies. Keep runtime config
here instead of beside each document to reduce duplication.

| File | Used by | Description |
| --- | --- | --- |
| `cognitive_loop.yaml` | `docs/case-studies/cognitive-loop/README.md` | Behavior + telemetry knobs for the recursive loop. |
| `log_analyzer_config.yaml` | `docs/case-studies/log-analyzer/README.md` | Stream classification and alert thresholds. |
| `reward_config.yaml` | Planner/Reinforce case studies | Reward shaping parameters for RL agents. |
| `training_workflow.yaml` | Planner/Reinforce case studies | Canonical training pipeline. |

When creating a new SRS that needs bespoke config, prefer referencing one of
these or adding a new file in this directory.
