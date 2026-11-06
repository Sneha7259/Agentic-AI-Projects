# Agentic AI Project Pack — M1-P5 + M1-P6

Two independent Flask applications upgraded from one-shot AI utilities into **tool-using, multi-step agentic prototypes**. Both expose their agent execution trace so users can inspect what the system did and why.

## Project 1 — M1-P5: Hallucination-Aware Information Agent (Verity)

### Goal
Answer questions only when the available evidence provides meaningful support. Distinguish high-confidence evidence matches, inference, and potentially unsupported responses. Abstain rather than fabricate when support is weak.

### Agent architecture
1. **Planner** — interprets the question and frames the evidence lookup.
2. **Evidence Retrieval Tool** — searches the local evidence corpus and returns candidate passages.
3. **Evidence Verification Tool** — measures question-to-passage support and records matched terms.
4. **Critic / Reflection Agent** — evaluates whether the evidence is strong enough to answer; rejects weakly supported cases.
5. **Response Policy** — produces an answer with evidence provenance and uncertainty label, or explicitly abstains.

### Why it is agentic
The response is produced by an orchestrated sequence of decisions and tool calls, not a single template response. The critic controls whether the answer stage is allowed to proceed. The UI displays the execution trace.

### Current prototype limitation
The corpus is a small local demo library and the verifier uses lexical overlap heuristics. The displayed score is **not a calibrated probability** and does not prove truth. For a production system, connect vetted search/database tools, use semantic retrieval and claim-level entailment checks, calibrate on an evaluation set, retain provenance, and require human review for high-stakes topics.

### Run
```bash
cd M1-P5-hallucination-assistant
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5001

## Project 2 — M1-P6: Personalized News Intelligence Agent (Briefly)

### Goal
Generate a source-linked digest based on selected interests, while reducing irrelevant and duplicate stories.

### Agent architecture
1. **Preference Planner** — converts the user's selected topics into category-specific search tasks.
2. **News Search Tools** — calls the GNews search endpoint once per requested category when `GNEWS_API_KEY` is configured; otherwise uses clearly labelled demo stories.
3. **Relevance & Deduplication Agent** — classifies candidates, filters unrelated items, and suppresses near-duplicate headlines.
4. **Ranking Agent** — prioritizes matching and timestamped stories.
5. **Summarization Agent** — creates concise extracts from publisher-provided descriptions.
6. **Quality Review Agent** — checks required fields and source URL provenance before the digest is returned.

### Why it is agentic
The planner creates multiple search tasks, tools gather data, later agents make filtering and ranking decisions, and a final reviewer validates the output. The execution trace is visible in the UI.

### Run
```bash
cd M1-P6-personalized-news
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```
Optional live news: create a GNews API key and set `GNEWS_API_KEY` in your environment. Without it, the app uses labelled demo stories. Demo links are placeholders and must not be treated as live articles.
```bash
python app.py
```
Open http://127.0.0.1:5002

## Requirements
- Python 3.10+
- Flask 3.x
- Requests 2.x (P6 only)
- Internet access and a GNews API key for live P6 news retrieval

## Agentic AI vs. a basic chatbot
These projects demonstrate agentic patterns: planning, tool invocation, intermediate state, conditional decisions, reflection/quality checks, and observable traces. They are **bounded workflow agents**, not unrestricted autonomous agents. They do not execute arbitrary code, access private accounts, or take irreversible actions.

## Suggested future enhancements
- Replace lexical retrieval with embeddings + vector database (P5).
- Add a web search connector and source reputation metadata (P5).
- Add semantic claim-level verification and calibrated confidence (P5).
- Persist user interests with consent and provide a daily scheduler (P6).
- Add multiple news providers, freshness scoring, language preferences, and user feedback (P6).
- Add authentication, rate limits, structured logs, tests, and deployment configuration before production.

## Safety and privacy
No user profile is persisted by these demos. Do not submit sensitive personal data. Review GNews provider terms and rate limits before deployment. Both apps are educational prototypes, not production fact-checking or financial/news advisory systems.
