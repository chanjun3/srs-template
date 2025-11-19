# Overview artefacts

This folder hosts high-level narratives that set context for the entire programme:

- `AI_Agent_NotionDB_Architecture_Requirements.md` – asynchronous Notion DB hub + Supabase/Qdrant mesh.
- `AI_Cognitive_Framework_Report.md` – recursive reasoning loop vision and governance.
- `glossary.md` – authoritative list of programme terminology.

## Architecture summary
- Reference stack: Supabase (structured data) × Qdrant/Weaviate (vector search) × Notion (human UI).
- Cognitive Loop: Pause & Reframe → Structured Articulation → Dialectical Defense → Forward Expansion.
- Governance: Collector/Normalizer/Analyzer separation with configs under `docs/case-studies/config/`.

## Branch policy
- `main` **must remain deployable**; only reviewed PRs are merged.
- Any SRS change (global or local) requires a pull request with lint + CI green.
- Hotfixes follow the same rule; no direct pushes to `main`.

Add new overview documents here when they apply across multiple systems or personas, and link new
terminology back to [`glossary.md`](glossary.md).
