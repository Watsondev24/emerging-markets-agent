# Frontier — Emerging Markets Intelligence Agent

An institutional-grade emerging markets research platform powered by LangGraph, Google Gemini, and Tavily. Built for investors, strategists, and operators who need rigorous, data-driven analysis on emerging market opportunities.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![LangGraph](https://img.shields.io/badge/LangGraph-latest-green) ![Gemini](https://img.shields.io/badge/Gemini-Flash-orange) ![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal)

---

## What It Does

Frontier takes a natural language query about an emerging market opportunity and runs it through a multi-step research pipeline that:

1. **Classifies the query** — routes it to either a direct Gemini answer or the full research pipeline
2. **Runs 6 parallel research nodes** via live Tavily web search:
   - Macroeconomic context
   - Political risk & governance
   - Sector opportunity & market size
   - Exit landscape & comparable deals
   - Currency & FX risk
   - Market timing & maturity
3. **Aggregates all research** into a unified context
4. **Checks the regulatory environment** for FDI rules and licensing requirements
5. **Writes a draft market entry brief** with structured chart data
6. **Reflects and rewrites** — a critique pass improves the draft before final output

The result is a structured **Market Entry Brief** with charts, risk tables, market comparison data, and a clear investment verdict.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser                               │
│              Frontier Chat UI                            │
│           frontier.html · localhost:3000                 │
└─────────────────────┬───────────────────────────────────┘
                      │ POST /analyse
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI                               │
│                    api.py                                │
│              Backend · localhost:8000                    │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │                   Router                         │   │
│   │   Classifies: pipeline / direct / out_of_scope   │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   LangGraph                              │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              NODE 1: parse_query                 │   │
│   │   Gemini extracts market, sector, query type,    │   │
│   │         investor type, time horizon              │   │
│   └──────────────────────┬──────────────────────────┘   │
│                           │ parallel fan-out via Send()  │
│        ┌──────────────────┼──────────────────┐          │
│        ▼                  ▼                  ▼           │
│  ┌───────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  NODE 2A  │    │   NODE 2B   │    │   NODE 2C   │    │
│  │macro_node │    │political_   │    │ sector_node │    │
│  │GDP,       │    │node         │    │TAM, growth, │    │
│  │inflation, │    │Governance,  │    │key players  │    │
│  │rates      │    │stability    │    │             │    │
│  └─────┬─────┘    └──────┬──────┘    └──────┬──────┘    │
│        │                 │                  │            │
│  ┌─────▼─────┐    ┌──────▼──────┐    ┌──────▼──────┐    │
│  │  Tavily   │    │   Tavily    │    │   Tavily    │    │
│  │  search   │    │   search    │    │   search    │    │
│  └───────────┘    └─────────────┘    └─────────────┘    │
│        │                 │                  │            │
│        └──────────────────┼──────────────────┘          │
│                           │ (also parallel)              │
│        ┌──────────────────┼──────────────────┐          │
│        ▼                  ▼                  ▼           │
│  ┌───────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  NODE 2D  │    │   NODE 2E   │    │   NODE 2F   │    │
│  │ exit_node │    │   fx_node   │    │timing_node  │    │
│  │Exit paths,│    │Currency &   │    │Market entry │    │
│  │comparable │    │FX risk,     │    │timing &     │    │
│  │deals      │    │hedging      │    │maturity     │    │
│  └─────┬─────┘    └──────┬──────┘    └──────┬──────┘    │
│        │                 │                  │            │
│  ┌─────▼─────┐    ┌──────▼──────┐    ┌──────▼──────┐    │
│  │  Tavily   │    │   Tavily    │    │   Tavily    │    │
│  │  search   │    │   search    │    │   search    │    │
│  └───────────┘    └─────────────┘    └─────────────┘    │
│                           │                              │
│                    fan-in — waits for all 6              │
│                           ▼                              │
│   ┌─────────────────────────────────────────────────┐   │
│   │             NODE 3: aggregate_node               │   │
│   │      Merges all 6 research outputs               │   │
│   └──────────────────────┬──────────────────────────┘   │
│                           ▼                              │
│   ┌─────────────────────────────────────────────────┐   │
│   │            NODE 4: regulatory_node               │   │
│   │    FDI rules, licensing, compliance              │   │
│   │              + Tavily search                     │   │
│   └──────────────────────┬──────────────────────────┘   │
│                           ▼                              │
│   ┌─────────────────────────────────────────────────┐   │
│   │              NODE 5: brief_node                  │   │
│   │  Gemini synthesises research → draft report      │   │
│   │         + structured chart data                  │   │
│   └──────────────────────┬──────────────────────────┘   │
│                           ▼                              │
│   ┌─────────────────────────────────────────────────┐   │
│   │             NODE 6: reflect_node                 │   │
│   │   Gemini critiques draft → rewrites final        │   │
│   └──────────────────────┬──────────────────────────┘   │
└──────────────────────────┼──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   JSON Response → UI                     │
│   Market Entry Brief · Charts · Maps · Risk Tables       │
└─────────────────────────────────────────────────────────┘
```

**Node legend:**
- 🟣 Gemini nodes (1, 5, 6) — LLM reasoning and synthesis
- 🟢 Parallel research nodes (2A–2F) — all run simultaneously
- 🟩 Tavily live search — real-time web data for each node
- 🟠 Regulatory node (4) — FDI and compliance check

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent orchestration | LangGraph |
| Language model | Google Gemini (gemini-3-flash-preview) |
| Live web search | Tavily |
| API backend | FastAPI |
| Query routing | Custom router with Gemini classification |
| Conversation memory | Browser-side sliding window (last 3 turns) |
| Frontend | Vanilla HTML/CSS/JS (frontier.html) |

---

## Prerequisites

- Python 3.11 or higher
- A Google Gemini API key — [get one here](https://aistudio.google.com/)
- A Tavily API key — [get one here](https://tavily.com/)

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/Watsondev24/emerging-markets-agent.git
cd emerging-markets-agent
```

### 2. Install dependencies

```bash
pip install langgraph langchain-google-genai langchain-core tavily-python fastapi uvicorn python-dotenv httpx pydantic rich
```

### 3. Create your `.env` file

The `.env` file is hidden by default. Create it directly in the terminal:

```bash
nano .env
```

Add your keys:

```
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Press **Ctrl + X → Y → Enter** to save.

---

## Running the App

You need two terminal windows.

**Terminal 1 — start the API:**

```bash
cd emerging-markets-agent
uvicorn api:app --reload
```

You should see: `Application startup complete`

**Terminal 2 — start the UI server:**

```bash
cd emerging-markets-agent
python3 -m http.server 3000
```

**Open your browser:**

```
http://localhost:3000/frontier.html
```

---

## Usage

Type any emerging markets query into the input field. Examples:

- `"Should we expand our fintech platform into Indonesia?"`
- `"What are the best emerging markets for SaaS in 2025?"`
- `"Assess the renewable energy opportunity in Vietnam"`
- `"Compare Nigeria vs Kenya for digital payments"`
- `"What is the regulatory environment for FDI in Bangladesh?"`

The agent will run the full 6-node research pipeline and return a structured **Market Entry Brief** with:

- Executive summary and investment verdict
- Macroeconomic context with GDP data
- Sector opportunity analysis
- Risk assessment table
- Exit landscape and comparable deals
- Currency & FX risk analysis
- Market timing assessment
- Regulatory landscape
- Interactive charts

### Conversation Memory

The agent remembers the last 3 turns of your conversation. You can ask follow-up questions naturally:

```
You: "fintech in Indonesia"
→ [full pipeline runs]

You: "what are the key risks for that market?"
→ [agent understands "that market" = Indonesia]

You: "how does the regulatory environment compare to Vietnam?"
→ [agent uses prior context to compare]
```

### Query Routing

Not every query runs the full pipeline. The router classifies each query first:

- **Pipeline** — live research required (market entry, risk assessment, opportunity scan)
- **Direct** — answered from Gemini's knowledge (definitions, concepts, follow-ups)
- **Out of scope** — politely declined (cooking, sports, personal advice)

---

## Project Structure

```
emerging-markets-agent/
├── api.py              # FastAPI backend — routes queries, runs pipeline
├── graph.py            # LangGraph graph wiring with parallel fan-out
├── nodes.py            # All 11 pipeline nodes
├── router.py           # Query classifier (pipeline / direct / out_of_scope)
├── state.py            # AgentState TypedDict shared across all nodes
├── tools.py            # Fallback stub data tools (used if Tavily fails)
├── main.py             # Terminal interface for testing
├── frontier.html       # Full chat UI with charts, maps, and panels
└── .env                # API keys (never commit this)
```

---

## API

The FastAPI backend exposes one main endpoint:

### `POST /analyse`

```json
{
  "query": "Should we enter the Nigerian fintech market?",
  "conversation_history": []
}
```

**Response:**

```json
{
  "report": "# Market Entry Brief: Nigeria — Fintech\n...",
  "chart_data": { "risk_chart": {...}, "market_size_chart": {...} },
  "market": "Nigeria",
  "sector": "fintech",
  "query_type": "single_market",
  "route": "pipeline",
  "errors": []
}
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## Stopping and Restarting

To stop both servers:

```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

To restart:

```bash
cd emerging-markets-agent
uvicorn api:app --reload
# (new terminal tab)
python3 -m http.server 3000
```

---

## Notes

- **Response time** — single market queries take 20–40 seconds, broad queries (all emerging markets) take 60–90 seconds due to 6 parallel Tavily searches + 2 Gemini calls
- **Tavily fallback** — if Tavily fails or rate limits, the agent falls back to stub data in `tools.py` so the pipeline always completes
- **API costs** — each full pipeline query makes ~8 Tavily searches and 2–3 Gemini calls. Keep an eye on usage if running many queries

---

## Built By

René Bossa & Marili Kammenou
