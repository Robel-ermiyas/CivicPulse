# Databricks AI Capstone Strategy — Top-3 Blueprint (Free Edition Only)

*Prepared as a competition strategist / judge working backward from "what makes a judge sit up" while staying inside real Free Edition constraints (serverless-only, one 2X-Small SQL warehouse, ≤5 concurrent job tasks, one AI Search endpoint/1 search unit, ≤3 Databricks Apps, one Lakebase project, restricted outbound internet, fair-use compute quotas that can suspend your workspace for the day if exceeded).*

---

## 1. Judge's Lens: What Actually Wins

Every cohort produces 30–80 versions of "chatbot + RAG over some PDFs + a Streamlit-ish app." The ones that place Top 3 share four traits judges reward every time:

1. **The agent does something a human would otherwise have to do manually** — not just answer questions.
2. **Spark and Lakebase are load-bearing**, not decorative. If you could delete Spark and replace it with `pandas.read_csv`, judges notice.
3. **The unstructured data is genuinely irregular** (scanned forms, meeting minutes, inconsistent PDFs) — clean structured-only "unstructured data" (like a single tidy article) reads as checkbox compliance.
4. **The demo has one moment where the audience visibly reacts** — usually the agent taking an action that changes something real, not another answer bubble.

Movies, trips, stocks, and jobs are the four most oversaturated demo categories in every hackathon on earth (every bootcamp, every Kaggle challenge, every "AI agent tutorial" on YouTube builds one of these). Research/Learning Copilot is slightly less saturated but is *inherently* a read-only pattern — "find sources, summarize, quiz me" — which makes the WRITE/action requirement feel bolted on (saving notes, creating flashcards) rather than essential.

---

## 2. 19 Candidate Ideas (Brainstormed Beyond the Official Five)

| # | Idea | One-line concept |
|---|------|-------------------|
| 1 | AI Movie Night Planner *(official)* | Recommends movies from mood/group prefs |
| 2 | AI Trip & Outdoor Activity Planner *(official)* | Plans trips using weather/terrain data |
| 3 | AI Research & Learning Copilot *(official)* | Summarizes papers, builds study plans |
| 4 | AI Stock Market Research Assistant *(official)* | Analyzes filings/news for tickers |
| 5 | AI Job Hunting Copilot *(official)* | Matches resumes to postings |
| 6 | **CivicPulse** — Legislative & City Council Tracking Copilot | Tracks bills/ordinances relevant to a user, drafts testimony |
| 7 | GrantPilot — Small Business Grant & Compliance Copilot | Matches SMBs to grants, tracks deadlines, drafts applications |
| 8 | AgroAdvisor — Farm Field Advisory Copilot | Combines weather/soil APIs + extension bulletins into field tasks |
| 9 | AccessScan — Website Accessibility Compliance Copilot | Scans sites against WCAG, files remediation tickets |
| 10 | RentGuard — Lease & Tenant Rights Copilot | Flags risky lease clauses, drafts dispute letters |
| 11 | DisasterLink — Local Emergency Resource Navigator | Matches residents to shelters/aid during disasters, logs requests |
| 12 | NonprofitIQ — Grant-Writing & Donor Intelligence Copilot | Mines 990 filings + LOIs, drafts donor outreach |
| 13 | OpenSourceOps — Maintainer Triage Copilot | Reads issues/docs, drafts labels, opens PRs/replies |
| 14 | CampusPath — Degree Planning & Registration Copilot | Plans course schedule, checks prerequisites, flags holds |
| 15 | PantryChef — Nutrition & Grocery Budget Copilot | Plans meals from pantry + nutrition data, builds shopping list |
| 16 | EventGuard — Outdoor Event Weather-Risk Copilot | Monitors weather risk for scheduled events, reschedules/notifies |
| 17 | PermitPath — Building Permit & Code Copilot | Matches renovation plans to local code, tracks permit status |
| 18 | ScholarshipMatch — Financial Aid Copilot for Students | Matches students to scholarships, tracks essays/deadlines |
| 19 | WarrantyVault — Product Recall & Warranty Copilot | Tracks owned products against recall feeds, files claims |

---

## 3. Scoring Matrix (1–10, brutally honest)

| Project | Problem Importance | Originality | Impact | Spark/DE | AI/Agent Depth | RAG/Unstructured | Databricks Fit | Free Edition Feasibility | Demo/Wow | **Top-3 Potential** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1. Movie Night | 3 | 2 | 3 | 4 | 4 | 4 | 5 | 9 | 4 | **Low** |
| 2. Trip Planner | 5 | 3 | 5 | 6 | 5 | 6 | 6 | 8 | 6 | **Medium-Low** |
| 3. Research Copilot | 6 | 4 | 6 | 5 | 5 | 8 | 6 | 8 | 5 | **Medium** |
| 4. Stock Assistant | 6 | 3 | 5 | 6 | 5 | 6 | 6 | 6 | 6 | **Medium-Low** |
| 5. Job Hunting | 6 | 3 | 6 | 6 | 5 | 6 | 6 | 8 | 5 | **Medium** |
| 6. **CivicPulse** | 9 | 9 | 9 | 8 | 9 | 8 | 9 | 8 | 9 | **Very High** |
| 7. GrantPilot | 8 | 7 | 8 | 7 | 8 | 7 | 8 | 7 | 7 | High |
| 8. AgroAdvisor | 7 | 7 | 7 | 7 | 7 | 6 | 7 | 6 | 6 | Medium-High |
| 9. AccessScan | 6 | 6 | 6 | 5 | 6 | 5 | 6 | 7 | 5 | Medium |
| 10. RentGuard | 8 | 6 | 8 | 6 | 7 | 7 | 7 | 8 | 7 | High |
| 11. DisasterLink | 9 | 7 | 9 | 7 | 7 | 6 | 7 | 5 | 8 | Medium-High (API access risky in emergencies) |
| 12. NonprofitIQ | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 5 | Medium |
| 13. OpenSourceOps | 6 | 6 | 6 | 5 | 7 | 5 | 6 | 8 | 6 | Medium |
| 14. CampusPath | 5 | 4 | 5 | 5 | 5 | 4 | 5 | 8 | 4 | Low-Medium |
| 15. PantryChef | 4 | 4 | 4 | 5 | 4 | 4 | 5 | 8 | 5 | Low |
| 16. EventGuard | 5 | 6 | 5 | 5 | 6 | 3 | 5 | 7 | 5 | Low-Medium |
| 17. PermitPath | 7 | 7 | 7 | 6 | 7 | 6 | 7 | 6 | 6 | Medium-High |
| 18. ScholarshipMatch | 6 | 4 | 6 | 5 | 5 | 5 | 5 | 8 | 4 | Low-Medium |
| 19. WarrantyVault | 4 | 5 | 4 | 4 | 5 | 4 | 5 | 7 | 4 | Low |

---

## 4. Benchmarking the Five Official Projects

**AI Movie Night Planner** — Strengths: trivially easy to get an MVP running; API access (TMDb) is simple and Free-Edition-friendly. Weaknesses: no serious structured/unstructured tension, low stakes, no compelling WRITE action beyond "save a watchlist." Originality is essentially zero — this is the canonical "first agent tutorial" project. **Top-3 potential: low.**

**AI Trip & Outdoor Activity Planner** — Strengths: naturally uses weather + terrain APIs, decent unstructured data (trail descriptions, reviews). Weaknesses: extremely common (every hackathon has 3–4 of these), the agent's "actions" (booking, itinerary building) are usually fake since real booking APIs are paid/gated. **Top-3 potential: medium-low.**

**AI Research & Learning Copilot** — Strengths: RAG is genuinely central, and it's the instructor's pick so grading familiarity may help partial credit. Weaknesses: it's structurally read-heavy — the WRITE side (notes, flashcards, study plans) feels bolted on rather than necessary, and "summarize documents" is the single most-built RAG demo in existence. **Top-3 potential: medium** — safest, least distinctive.

**AI Stock Market Research Assistant** — Strengths: rich structured data (prices, filings) and real third-party APIs (Alpha Vantage, SEC EDGAR). Weaknesses: judges have seen this pattern dozens of times, real trading actions are (correctly) usually disabled for legal/compliance reasons, so the WRITE tool ends up being "save this stock to a watchlist" — low stakes. **Top-3 potential: medium-low.**

**AI Job Hunting Copilot** — Strengths: clear, relatable pain point; resume PDFs are genuinely unstructured; job-board APIs exist. Weaknesses: resume-matching is a commodity ML problem now baked into LinkedIn/Indeed themselves, so it reads as "rebuilding a feature big platforms already ship." **Top-3 potential: medium.**

**Verdict on innovation/impact/depth/demo purely among the five:** AI Research & Learning Copilot is the strongest *of the five*, mainly because RAG is unavoidable rather than decorative — but it is still the "safe" choice, not a *winning* one, because every other team choosing the instructor's suggestion will build a structurally similar project.

**Can a new project realistically beat all five?** Yes — decisively, if it targets a domain where (a) the data is messy enough that Spark is required, not optional, (b) the agent's write-actions have real consequence (not "save to favorites"), and (c) the problem is one judges haven't watched pitched a dozen times already this semester.

---

## 5. The White Space

The five official ideas all live in **consumer convenience** (movies, trips, stocks, jobs, study habits) — domains with abundant clean APIs and low-stakes actions. The white space is **civic and regulatory information work**: government/legal/compliance domains where:

- Structured data is fragmented across agencies and update cadences (legislative calendars, bill statuses, vote records).
- Unstructured data is genuinely messy — meeting minutes, ordinance PDFs, testimony transcripts, agenda attachments — the kind of documents that actually *need* chunking, OCR-adjacent cleanup, and semantic retrieval to be usable.
- No consumer platform already solves this well (unlike movies/jobs/trips, which are dominated by Letterboxd, LinkedIn, Google Flights).
- An agent's write actions are *consequential*: tracking a bill on someone's behalf, drafting testimony before a real deadline, flagging a conflict between two competing ordinances.
- The demo has a built-in narrative arc: "a real vote is happening this week — watch the agent catch it and draft testimony before the deadline."

This is the basis for the winning pick below.

---

## 6. Top 3 Finalists

### Finalist A — CivicPulse (Legislative & City Council Tracking Copilot)
- **Pitch:** An agent that reads state bills and city council agendas the way a lobbyist's staffer would — tracking what matters to *you* and drafting your testimony before the deadline.
- **Problem:** Ordinary residents and small advocacy groups cannot realistically track legislation/ordinances relevant to them across dozens of bill updates, committee hearings, and meeting agendas a month — so they miss comment windows entirely.
- **Target users:** Engaged residents, renters, small-business owners, neighborhood associations, students studying public policy.
- **Why it matters:** Most policy that directly affects people's rent, schools, and streets is decided at the state/local level, invisibly, with public comment windows most people never see in time.
- **Existing alternatives:** FiscalNote/Quorum (enterprise-only, expensive), raw legislature websites (unsearchable, no personalization), city clerk portals (PDF dumps, zero tracking).
- **Solution:** Spark ingests bulk bill/ordinance data + PDFs, AI Search makes it semantically searchable, Lakebase stores user watchlists/profiles, agent reads bills relevant to the user's tracked topics and *drafts* public comment/testimony ready to submit, and logs tracked-issue state changes.
- **Why innovative:** Nobody in a typical cohort builds a civic-tech project; structured + irregular unstructured data tension is real, not manufactured.
- **Why it beats the official 5:** Real stakes, real deadlines, un-saturated domain, agent WRITE actions are consequential rather than cosmetic.
- **Free Edition feasibility:** High — Open States API is free/public with generous limits and offers **bulk data dumps** as an offline fallback if live API calls are restricted; volumes are small enough for a 2X-Small warehouse and single AI Search unit.

### Finalist B — GrantPilot (Small Business Grant & Compliance Copilot)
- **Pitch:** An agent that reads a small business's profile against hundreds of grant/RFP PDFs and drafts the application sections that match.
- **Problem:** Small businesses and nonprofits lose access to real funding because grant discovery and application-writing take specialized time they don't have.
- **Solution:** Spark processes grants.gov bulk XML + PDFs of guidelines; AI Search matches business profile to eligible grants; agent drafts narrative sections and tracks deadlines in Lakebase.
- **Free Edition feasibility:** High — grants.gov offers bulk downloadable XML/CSV as a built-in fallback to live API calls.
- **Trade-off vs CivicPulse:** Slightly less demo drama (no "vote this week" urgency), narrower emotional pull for a general judging panel.

### Finalist C — RentGuard (Lease & Tenant Rights Copilot)
- **Pitch:** An agent that reads a tenant's actual lease against real local housing law and flags what's illegal or negotiable.
- **Problem:** Most tenants sign leases with clauses that violate local law and never know it; legal aid is scarce and slow.
- **Solution:** Spark processes local housing-code corpora + user-uploaded lease PDFs (real unstructured, OCR-adjacent data); AI Search retrieves relevant statute passages; agent flags risky clauses and drafts a dispute letter, logging cases in Lakebase.
- **Free Edition feasibility:** Good, but carries **legal-advice liability framing risk** — must be scoped tightly as "informational, not legal advice," which slightly constrains how aggressively the agent can act.

---

## 7. The Winner: **CivicPulse**

CivicPulse wins on the composite of impact, originality, demo drama, Free Edition feasibility, and the fact that its WRITE actions (tracking issues, drafting testimony against a real public-comment deadline) are unambiguously consequential rather than decorative — the exact quality graders are told to look for and the exact quality most competing projects will lack.

---

## 8. CivicPulse — Full Technical & Product Blueprint

### A. Project Name
**CivicPulse** — *"Your Legislative Staffer, For Free."*

### B. 10-Second Pitch
"CivicPulse reads every new state bill and city council agenda the moment it drops, tells you the ones that actually affect your life, and drafts your public testimony before the comment window closes."

### C. Problem
State legislatures introduce thousands of bills per session; city councils publish dense agenda packets weekly. The people most affected — renters, small-business owners, parents, disabled residents — have no realistic way to monitor this firehose. Comment windows (often 48–72 hours before a vote) close before most people even learn a hearing happened. Today this is handled by paid lobbying platforms (FiscalNote, Quorum, CQ) that cost thousands of dollars a year, or manually by advocacy-group staff scanning PDFs by hand. Neither scales to an individual resident.

### D. Solution — Exact Workflow
1. User signs up in the Databricks App and creates a **profile**: home state/city, topics of interest (housing, schools, transit, small business, healthcare), and optionally uploads a short "who I am" statement (renter, business owner, parent, etc.) used to personalize testimony tone.
2. A scheduled Spark job ingests newly filed/updated bills (Open States bulk API/dump) and newly published local council agendas/minutes (uploaded or scraped PDFs) into a Bronze Delta table nightly.
3. Spark transforms raw bill text and PDF agenda text into a cleaned, chunked Silver layer; chunks are embedded and pushed to Databricks AI Search.
4. The user opens the app dashboard; it already shows a **personalized feed**: "3 new bills match your tracked topics this week," with plain-language summaries.
5. User clicks "Track" on a bill — this writes a row to Lakebase (`tracked_issues`).
6. As the bill/agenda item approaches a hearing or vote, the agent proactively (or on request) **drafts public comment/testimony** grounded in the actual bill text + the user's stated stake, and saves it as a draft record the user can edit and copy to submit.
7. User can ask the agent conversational follow-ups ("What's the actual fiscal impact of this bill? Has anything similar passed in nearby states?") — the agent retrieves semantically, reasons over structured vote-history data, and answers with citations to the actual bill sections.
8. Dashboard shows a **history view**: every tracked issue, its current status (introduced → committee → hearing scheduled → passed/failed), and every testimony draft the user has produced — a durable personal civic record.

---

## 9. Requirement Mapping

| Requirement | Exact Implementation |
|---|---|
| Spark pipeline | Nightly job: ingest Open States bulk bill dump + uploaded/scraped council PDFs → Bronze Delta; PySpark cleans/normalizes bill metadata (status, sponsor, topic tags), chunks bill/agenda text, dedupes → Silver Delta |
| Third-party API | Open States API (free, public, bill/legislator/vote data across all 50 states) — bulk-dump fallback if live calls are throttled |
| Unstructured data | Bill full text (HTML/text), city council agenda & minutes PDFs (often scanned/irregular formatting) |
| Data processing | Spark: text cleaning, section splitting, topic-tag extraction via keyword/embedding clustering, chunking (~500 tokens/chunk with overlap) |
| Embeddings | Databricks-hosted embedding model (foundation model API) run over Silver chunks, written to a Delta table with vector column |
| AI Search / semantic retrieval | Single Databricks AI Search endpoint/index over bill+agenda chunks (fits the one-endpoint/one-unit Free Edition limit) |
| RAG | Agent retrieves top-k chunks per query, grounds summaries/testimony drafts in retrieved bill text with section citations |
| Lakebase | Stores `users`, `tracked_issues`, `testimony_drafts`, `notifications` — relational app state, fast reads for the dashboard |
| Databricks App | Full frontend: onboarding, personalized feed, bill detail view, agent chat, tracked-issues dashboard, draft history |
| AI Agent | Tool-using agent (Mosaic AI Agent Framework / tool-calling LLM) orchestrating read + write tools below |
| Agent READ tools | `search_bills_semantic`, `get_bill_status`, `get_vote_history`, `get_user_profile` |
| Agent WRITE tools | `track_issue`, `save_testimony_draft`, `update_issue_status`, `create_notification` |

---

## 10. Data Architecture

**Sources → Bronze → Silver → Gold/Serving:**

- **Sources:** Open States bulk bill data (JSON/CSV), Open States API for incremental updates, user-uploaded or scraped city council agenda/minutes PDFs.
- **Spark ingestion:** A scheduled Databricks Job (serverless, within the 5-concurrent-task limit) pulls new/changed bills and drops raw JSON/PDF bytes into a Bronze Delta table (`bronze_bills`, `bronze_agendas`) with ingestion timestamps.
- **Bronze → Silver:** PySpark normalizes bill metadata into typed columns (bill_id, state, status, sponsor, topics, last_action_date); for PDFs, text is extracted (PyMuPDF/pdfplumber inside the Spark job or a lightweight UDF) and split into clean paragraphs.
- **Curated/Gold:** `gold_bill_summary` (one row per bill with plain-language summary generated once and cached), `gold_bill_chunks` (chunked text ready for embedding).
- **Unstructured pipeline:** chunking (~400–600 tokens, sentence-boundary aware) → embedding via Databricks foundation model API → written to a vector-enabled Delta table → synced to the single AI Search index.
- **Lakebase:** holds all user-specific relational state (profiles, tracked issues, drafts, notifications) — queried directly by the Databricks App backend for low-latency reads, separate from the analytical Delta/Spark side.
- **RAG:** agent query → AI Search retrieves top-k relevant chunks → chunks + structured bill metadata (from Gold tables, queried via Databricks SQL on the single warehouse) are assembled into the LLM context → grounded answer with citations.
- **Agent:** orchestrates the above read tools plus Lakebase write tools; runs as a tool-calling loop inside the Databricks App backend (or as a Model Serving-hosted agent endpoint within Free Edition's included serving quota).
- **Databricks App:** calls the agent endpoint and Lakebase directly; renders dashboard, feed, chat, and history views.

---

## 11. Agent Design

### Read Tools

| Tool | Purpose | Inputs | Outputs | Source | Why needed |
|---|---|---|---|---|---|
| `search_bills_semantic` | Find bills/agenda items relevant to a topic/question | query text, optional state/topic filter | ranked chunks + bill_id | AI Search index | Core RAG retrieval |
| `get_bill_status` | Get current structured status of a bill | bill_id | status, sponsor, last action, next hearing date | Gold Delta via SQL warehouse | Grounds "what's happening now" |
| `get_vote_history` | Compare to similar past bills | topic, state | list of past bills + outcomes | Gold Delta | Supports "has this passed elsewhere" reasoning |
| `get_user_profile` | Load the user's stated stake/topics | user_id | profile fields | Lakebase | Personalizes summaries/testimony tone |

### Write/Action Tools

| Tool | Purpose | Inputs | Outputs | Source | Why needed |
|---|---|---|---|---|---|
| `track_issue` | Add a bill/agenda item to user's watchlist | user_id, bill_id | confirmation, row id | Lakebase write | Core "do something" action |
| `save_testimony_draft` | Persist a drafted public comment | user_id, bill_id, draft text | draft id | Lakebase write | Real deliverable the user takes away |
| `update_issue_status` | Refresh a tracked issue when the bill's status changes | issue_id, new_status | confirmation | Lakebase write | Keeps dashboard current without manual polling |
| `create_notification` | Flag an approaching deadline to the user | user_id, message, due_date | notification id | Lakebase write | Drives the "before it's too late" value prop |

### Sample Agent Conversations

**1.**
> User: "Anything happening with rent control this session?"
> Agent → `search_bills_semantic("rent control", state=user.state)` → finds 2 bills
> Agent → `get_bill_status` on both → one has a hearing in 4 days
> Agent: "SB-214 caps annual rent increases at 5% and has a hearing this Thursday. Want me to draft testimony?"
> User: "Yes, I'm a renter, keep it short."
> Agent → `get_user_profile` → `save_testimony_draft` (grounded in retrieved bill text)
> Agent: "Draft saved — 140 words, cites Section 3. Review it in your dashboard before Thursday."

**2.**
> User: "Track that one."
> Agent → `track_issue` → confirms → `create_notification` for hearing date minus 1 day.

**3.**
> User: "Has anything like this passed anywhere nearby?"
> Agent → `get_vote_history("rent control")` → reasons over 3 prior state outcomes → answers with citations.

**4.**
> User: "What changed on the bills I'm tracking this week?"
> Agent → reads `tracked_issues` from Lakebase → `get_bill_status` per bill → `update_issue_status` where changed → summarizes diffs.

**5.**
> User: "Draft something for my small business, not as a renter."
> Agent → `get_user_profile` (multi-role) → retrieves business-relevant chunks → `save_testimony_draft` with business framing.

---

## 12. Databricks App Design

- **Onboarding:** location + topics + one-line "who I am" (renter/business/parent/etc.)
- **Feed (home):** cards — "3 new bills match your topics," plain-language one-liner, urgency badge (hearing in X days)
- **Bill detail view:** full status timeline, retrieved-and-cited summary, "Track" and "Draft testimony" buttons
- **Agent chat panel:** persistent side panel for free-form questions, always visible alongside structured views
- **Tracked issues dashboard:** table of tracked bills with live status, sortable by urgency
- **Draft history:** every testimony draft ever generated, editable, exportable/copyable
- **Notifications:** deadline countdown banners
- Visualizations: a simple bill-status funnel (introduced → committee → floor → passed/failed) and a topic-distribution chart of what the user tracks

---

## 13. The Killer Demo (3–5 min)

1. **Open cold:** "Right now, there's a bill in [state] that would change rent rules for millions of renters, and almost nobody who's affected knows it exists."
2. Open CivicPulse — dashboard already shows a personalized feed for a pre-seeded "renter" demo profile.
3. Click into the flagged bill — show the plain-language, cited summary generated from actual retrieved bill text.
4. Ask the agent live: "What's actually in Section 3?" — agent retrieves and answers with a citation, live, on stage.
5. Ask: "Draft my testimony" — agent produces a grounded draft in seconds.
6. Click **Track** — show the Lakebase-backed dashboard updating in real time with the new tracked issue and a countdown notification.
7. Switch to a second, pre-seeded profile (a small-business owner) and show the *same bill* producing a differently-framed testimony draft — proving personalization is real, not templated.
8. **WOW moment:** show the actual hearing date is 2 days away on screen, and the draft is already sitting ready to submit.
9. Close: "This is a $10,000/year lobbying-platform capability, built for free, and every draft is grounded in the actual bill text — not a guess."

---

## 14. Free Edition Architecture Audit

| Concern | Risk | Workaround |
|---|---|---|
| Serverless compute quota | Nightly Spark job could exceed fair-use if scheduled too frequently | Run ingestion once/day, keep job scoped to *changed* bills only (incremental, not full re-scan) |
| One 2X-Small SQL warehouse | Concurrent dashboard queries could queue | Keep Gold tables small/pre-aggregated; cache bill summaries so the app rarely hits the warehouse live |
| ≤5 concurrent job tasks | Parallel state ingestion could exceed | Sequence states/batches rather than fanning out all 50 states at once; demo can scope to 2–3 states for the competition build |
| One AI Search endpoint/1 unit | Index size limits | Cap the corpus to actively tracked topics + recent session bills, not the full historical archive |
| One Lakebase project | All relational state must share one project | Fine — CivicPulse only needs one relational database; single project is sufficient |
| ≤3 Databricks Apps | Need only 1 app | No conflict |
| Restricted outbound internet | Open States live API calls might be blocked from the workspace | Use Open States' downloadable bulk data dump, ingested once via upload, refreshed periodically by the student outside the platform if live calls fail |
| Model serving | No dedicated GPU/custom endpoints assumed | Use Databricks' included foundation model API (pay-per-token within free quota) for embeddings + agent LLM calls, not a self-hosted model |
| Fair-use suspension risk | Heavy embedding of a huge corpus in one run could trip quotas | Chunk-and-embed incrementally (batch nightly), not one giant backfill job |

**No component of this design depends on enterprise-only or paid infrastructure.** Everything maps to Free Edition's stated serverless/AI Search/Lakebase/Apps capabilities.

---

## 15. Data Sources & APIs

| Source | Data | Free/Paid | Auth | Limits | Refresh | Free Edition Access | Backup |
|---|---|---|---|---|---|---|---|
| Open States API/bulk data | Bill text, status, sponsors, votes (all 50 states) | Free, public | API key (free registration) | Reasonable rate limits | Nightly incremental | Should work via HTTPS; verify against allowed domains | Downloadable bulk JSON/CSV dump, uploaded once |
| City council portals (e.g., Legistar-based sites) | Agenda/minutes PDFs | Free, public | None typically | Varies by city | Weekly | May require manual download if scraping is blocked | Student manually downloads a handful of PDFs for the demo city |
| Databricks foundation model API | Embeddings + agent LLM | Included in Free Edition quota | Workspace-native | Fair-use quota | On demand | Native, no external call needed | N/A |

---

## 16. AI Evaluation Plan

- **Retrieval quality:** manually curated set of 15–20 test questions with known correct bill sections; measure hit@k.
- **Groundedness/citation accuracy:** spot-check that every generated summary/testimony cites a real retrieved chunk, not a hallucinated section number.
- **Tool-selection accuracy:** log agent tool calls against a hand-labeled expected-tool set for ~10 scripted conversations.
- **Action success rate:** % of `track_issue`/`save_testimony_draft` calls that complete without error and are reflected correctly in Lakebase.
- **Hallucination rate:** sample outputs, check any factual claim about bill content against source text.
- **Latency:** time from user question to grounded answer (target <8s for judge-facing demo reliability).

---

## 17. MVP vs Competition vs Stretch

**MVP:** Spark ingestion of 1–2 states' bills → chunk/embed → AI Search → Lakebase with `track_issue` and `save_testimony_draft` → minimal app with feed + chat + tracked list.

**Competition version:** adds council-agenda PDFs (true irregular unstructured data), vote-history comparison tool, notification/deadline system, polished multi-view app, second demo persona (business owner) to prove personalization.

**Stretch:** multi-state expansion, topic-clustering visualization, "similar bill elsewhere" auto-suggestions, email-style export of testimony drafts.

---

## 18. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Open States live API blocked from workspace | Use bulk-download fallback, ingest via upload |
| Free Edition compute quota exhausted before demo | Rehearse/build early in the week, keep nightly job small and incremental, avoid re-running full backfills |
| PDF text extraction messy (scanned agendas) | Scope demo city to one with clean digital agendas; keep OCR as stretch only |
| LLM hallucinates bill content | Enforce citation-required prompting; refuse to answer ungrounded claims |
| Agent picks wrong tool mid-demo | Script and rehearse the 3–5 demo conversations exactly; keep temperature low for agent calls |
| Scope creep (all 50 states, every city) | Explicitly cap MVP/competition build to 2–3 states, 1 demo city |
| Legal-sounding claims in testimony drafts | Frame all drafts as "informational draft, review before submitting," never as legal advice |

---

## 19. Development Roadmap

- **Phase 1 — Architecture:** finalize schema for Bronze/Silver/Gold, Lakebase tables, agent tool contracts.
- **Phase 2 — Data Engineering:** build Spark ingestion for Open States bulk data, land Bronze/Silver.
- **Phase 3 — Unstructured + Retrieval:** add council PDF ingestion, chunk/embed, stand up AI Search index.
- **Phase 4 — Lakebase:** implement `users`, `tracked_issues`, `testimony_drafts`, `notifications` tables + CRUD.
- **Phase 5 — Agent:** implement read/write tools, test scripted conversations.
- **Phase 6 — Databricks App:** build feed, bill detail, chat panel, dashboard, history views.
- **Phase 7 — Evaluation:** run retrieval/groundedness/tool-accuracy checks, fix gaps.
- **Phase 8 — Competition polish:** second persona, visualizations, rehearsed demo script, README + architecture diagram.

Prioritized so that if time runs out after Phase 5–6, you already have a complete, demoable, requirement-satisfying project.

---

## 20. Final Competitive Score — CivicPulse

| Dimension | Score | Why |
|---|--:|---|
| Problem importance | 14/15 | Directly affects rent, schools, local rights; real deadlines |
| Originality | 14/15 | No civic-tech project in the official set or typical cohort pool |
| Real-world impact | 14/15 | Democratizes a genuinely paid, gatekept capability |
| Data engineering | 9/10 | Multi-source ingestion, irregular PDFs, incremental Spark pipeline |
| AI/agent engineering | 14/15 | Read+write tools with real consequence, multi-step grounded reasoning |
| Databricks integration | 9/10 | Spark, Lakebase, AI Search, App, Jobs all load-bearing |
| Free Edition feasibility | 9/10 | Fits every stated quota; API has a genuine offline fallback |
| Demo/wow factor | 9/10 | Live grounded citation + real deadline countdown is a strong beat |
| **Total** | **92/100** | |

---

## 21. The Final Bet

**Yes.** If I had one shot at Top 3 on Free Edition, I would bet on CivicPulse specifically because it wins on the axis judges reward most and competitors chronically underweight: **consequential agent actions in an unsaturated domain with genuinely messy data**, not "cleverer prompting on the same five ideas everyone else is pitching." Every architectural piece — Spark, AI Search, Lakebase, the App, the agent's read/write split — earns its place naturally instead of being present to check a rubric box, and the demo has a built-in ticking clock that no movie/trip/stock/job pitch can manufacture. The main execution risk is scope discipline (cap states/cities early) and outbound-API access, both of which have concrete, tested workarounds above rather than open questions.
