# Data Requirements：Supabase / Qdrant / Notion

## DR-1 Supabase Schema

### Table: agent_logs

- id (uuid)
- agent_type (text)
- raw_log (jsonb)
- timestamp (timestamptz)

### Table: run_metadata

- id
- model_name
- token_used
- execution_time
- error_flag

---

## DR-2 Qdrant Schema

- vector (1536次元)
- metadata:
  - log_id
  - agent_type
  - category（error / fix / plan）

---

## DR-3 Notion DB Schema

- Title  
- Tags  
- Markdown Content  
- Supabase Log Link  
- Similarity Score  
