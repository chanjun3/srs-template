# Documentation catalogue

Curated inventory of every artefact that now lives under `docs/` (plus referenced
configs).
Use this table to cross-link PRDs, find canonical SRS, or delegate reviews by
role.

| Domain | Artefact | Path | Notes |
| --- | --- | --- | --- |
| Overview | AI Agent NotionDB Architecture Requirements | `docs/overview/AI_Agent_NotionDB_Architecture_Requirements.md` | Notion-centric async data plane. |
| Overview | AI Cognitive Framework Report | `docs/overview/AI_Cognitive_Framework_Report.md` | Vision deck for recursive reasoning loops. |
| Templates · 3-layer | Architecture Overview | `docs/templates/3layer/architecture_overview.md` | Diagram + description of the reference 3-layer stack. |
| Templates · 3-layer | Functional Requirements | `docs/templates/3layer/functional_requirements.md` | Feature-level contract for the reference implementation. |
| Templates · 3-layer | Non-Functional Requirements | `docs/templates/3layer/non_functional_requirements.md` | SLAs, observability, and compliance |
|   |   |   | for the template. |
| Templates · 3-layer | Integration Requirements | `docs/templates/3layer/integration_requirements.md` | API / event bus integration handshake. |
| Templates · 3-layer | Data Schema | `docs/templates/3layer/data_schema.md` | Canonical storage layout for telemetry + state. |
| Templates · 3-layer | Quality Assurance | `docs/templates/3layer/quality_assurance.md` | Validation and release gate checklist. |
| Requirements · Non-functional | Cloud Native Deployment Strategy | `docs/requirements/non-functional/cloud_native_deployment_strategy.md` |   |
|   |   |   | Tactical platform guidance. |
| Requirements · Data | Cognitive Logging Architecture | `docs/requirements/data/CognitiveLoggingArchitecture.md` | Logging + analytics reference design. |
| Requirements · Integration | Serverless Execution Architecture | `docs/requirements/integration/Serverless_Execution_Architecture.md` |   |
|   |   |   | Integration profile for serverless surfaces. |
| Requirements · Functional | PlannerAgent Local SRS | `docs/requirements/functional/planner/Local_SRS.md` | Task decomposition contract. |
| Requirements · Functional | CriticAgent Local SRS | `docs/requirements/functional/critic/Local_SRS.md` | Review criteria aligned with QA/governance. |
| Requirements · Functional | CoderAgent Local SRS | `docs/requirements/functional/coder/Local_SRS.md` | Implementation guardrails for code changes. |
| Requirements · Functional | ReviewerAgent Local SRS | `docs/requirements/functional/reviewer/Local_SRS.md` | Final review checkpoints and outcomes. |
| Requirements · Functional | OrchestratorAgent Local SRS | `docs/requirements/functional/orchestrator/Local_SRS.md` | Multi-agent flow orchestration rules. |
| Requirements · Functional | ResearchAgent Local SRS | `docs/requirements/functional/research/Local_SRS.md` | Evidence-based research workflow. |
| Governance | Branch Management Requirements | `docs/governance/Branch_Management_Requirements.md` | Git/branching roles and quality gates. |
| Governance | Data Utilization Policy SRS | `docs/governance/Data_Utilization_Policy_SRS.md` | Data residency / access control policies. |
| Assurance | CI/CD Pipeline SRS | `docs/assurance/CI_CD_Pipeline_SRS.md` | Platform guardrails and automation coverage. |
| Assurance | AI Literacy Development System | `docs/assurance/AI_Literacy_Development_System_SRS.md` | QA blueprint for the education / knowledge system. |
| Case study | AI Cognitive Loop | `docs/case-studies/cognitive-loop/README.md` | Detailed SRS for recursive cognitive loop agent. |
| Case study | Corporate Activity Watcher Agent | `docs/case-studies/corporate-activity-watcher/README.md` | Compliance monitoring assistant. |
| Case study | IaC Integration | `docs/case-studies/iac-integration/README.md` | Infra-as-code alignment SRS. |
| Case study | Log Analyzer Agent | `docs/case-studies/log-analyzer/README.md` | Streaming log triage agent. |
| Case study | MacroSignal Intelligence | `docs/case-studies/macrosignal-intelligence/README.md` | Macro-economic research copilot. |
| Case study | Planner Agent (Q-learning) | `docs/case-studies/planner-qlearning/README.md` | Reinforcement-based planning agent spec. |
| Case study | Reinforce Trainer Agent | `docs/case-studies/reinforce-trainer/README.md` | Training supervisory agent. |
| Case study | Valuation Feedback Analyzer | `docs/case-studies/valuation-feedback/README.md` | Investment feedback assessor. |
| Config | Cognitive Loop Workflow | `docs/case-studies/config/cognitive_loop.yaml` | Loop governance parameters referenced by the SRS. |
| Config | Log Analyzer Config | `docs/case-studies/config/log_analyzer_config.yaml` | Runtime config paired with the log analyzer case study. |
| Config | Reward Config | `docs/case-studies/config/reward_config.yaml` | Reinforcement tunes for trainer / planner agents. |
| Config | Training Workflow | `docs/case-studies/config/training_workflow.yaml` | Standardized training pipeline description. |

> ℹ️ Keep this catalogue alphabetized inside each domain to minimise merge
> conflicts.
