# AI Workflows

## 1. Command decomposition
`POST /api/command/preview`
1. Prompt arrives ("Launch Chapter 3 with Nano integration, Flipkart listing, and website release.")
2. Knowledge base retrieval: keyword-scored top documents are injected as context (swap-in point for Qdrant vector search: `command_center._rag_context`).
3. Engine:
   - **LLM mode** (OPENAI_API_KEY set): strict JSON contract, team roster and skill map in the system prompt, owners matched to skills.
   - **Offline mode**: deterministic template engine recognizes chapter launches, robot launches and marketplace listings, producing the same schema.
4. Plan returns with totals (epics/stories/tasks/subtasks/hours/dependencies) for human review. Nothing is committed.

`POST /api/command/execute`
5. On approval: items created in hierarchy order, owners notified, dependencies linked by title, every item pushed to Jira (when configured), audit logged.

## 2. Comment intelligence
Every comment is scanned (`ai_engine.analyze_comment`) for four signals: blocker, risk, dependency, urgent. Hits attach flags to the comment, surface in the executive risk feed, and notify all leads and admins. Keyword rules ship by default; swap in an LLM classification call in the same function for higher recall.

## 3. Workload suggestions
The Workload Engine computes remaining-estimate vs weekly capacity per person. When someone exceeds 90% and a teammate sits under 60%, it proposes skill-matched moves of unstarted tasks, each with a human-readable reason and one-click apply.

## 4. Document pipeline
Text uploads (.txt .md .csv .json) are indexed immediately. Binary formats (PDF/DOCX/PPT) are stored; wire an extraction step (e.g. pypdf, python-docx) into `misc.upload` to feed them to the same retrieval path.
