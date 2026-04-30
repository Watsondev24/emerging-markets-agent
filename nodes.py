# nodes.py
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient
from state import AgentState
from tools import get_macro_indicators, get_political_risk, get_sector_data, get_regulatory_environment


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.3,
    )


def get_tavily():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)


def tavily_search(query: str, max_results: int = 3) -> str:
    try:
        client = get_tavily()
        if not client:
            return ""
        results = client.search(query=query, max_results=max_results)
        snippets = []
        for r in results.get("results", []):
            title = r.get("title", "")
            content = r.get("content", "")
            url = r.get("url", "")
            snippets.append(f"Source: {title} ({url})\n{content}")
        return "\n\n---\n\n".join(snippets)
    except Exception as e:
        print(f"    [Tavily error: {e}]")
        return ""


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", str(content))
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", str(item)))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def clean_json(raw: str) -> str:
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


# ---------------------------------------------------------------------------
# NODE 1: parse_query
# ---------------------------------------------------------------------------

FRONTIER_SYSTEM_PROMPT = """You are Frontier, an institutional-grade emerging markets intelligence platform built by AskMarketIQ.

Your sole purpose is to provide rigorous, data-driven analysis on:
- Emerging market investment opportunities (India, Brazil, Nigeria, Vietnam, Indonesia, Mexico, Egypt, Pakistan, Kenya, Bangladesh, Philippines, Ethiopia, Colombia, Argentina, China, Southeast Asia, Sub-Saharan Africa, Latin America, Middle East, and more)
- Macroeconomic analysis, GDP trends, inflation, monetary policy
- Sector opportunities: fintech, SaaS/cloud, e-commerce, energy, consumer, infrastructure
- Political risk, regulatory environments, FX/currency risk
- Market timing, maturity curves, entry signals
- M&A activity, comparable deals, exit landscapes
- Investment strategy for FDI, portfolio investors, and startups
- Developed markets (UK, US, Europe, etc.) when discussed in the context of EM investment strategy or comparison

You do NOT answer questions outside this scope. If asked about cooking, sports, personal advice, general trivia, entertainment, or anything unrelated to markets and investment, you must politely decline and redirect.

Always respond as a senior analyst at a top-tier emerging markets investment firm — precise, evidence-based, and actionable."""


def parse_query(state: AgentState) -> dict:
    print("\n[Node 1] Parsing query + classifying intent...")
    llm = get_llm()
    query = state["query"]
    history = state.get("conversation_history", "")
    history_block = f"\n\nCONVERSATION HISTORY (use to understand follow-up questions):\n{history}" if history else ""

    # ── Scope check ──
    scope_messages = [
        SystemMessage(content=f"""{FRONTIER_SYSTEM_PROMPT}{history_block}

Your task is to classify whether the user's query is within Frontier's scope.

Respond with ONLY valid JSON:
{{
  "in_scope": true,
  "refusal_message": null
}}

If the query IS in scope (markets, investment, economics, geopolitics, sectors, currencies, any country in an investment/economic context, or a follow-up to a prior finance discussion): set in_scope to true, refusal_message to null.

If the query is NOT in scope (recipes, sports, personal advice, trivia, entertainment, etc.): set in_scope to false and write a short, professional refusal_message that redirects the user to Frontier's purpose. Keep it under 2 sentences."""),
        HumanMessage(content=query)
    ]

    scope_response = llm.invoke(scope_messages)
    scope_raw = clean_json(extract_text(scope_response.content))

    try:
        scope = json.loads(scope_raw)
        in_scope = scope.get("in_scope", True)
        refusal_message = scope.get("refusal_message", None)
    except Exception:
        in_scope = True
        refusal_message = None

    if not in_scope:
        print(f"    Out of scope query. Refusing.")
        return {
            "market": "N/A",
            "sector": "N/A",
            "query_type": "direct",
            "time_horizon": "medium_term",
            "investor_type": "general",
            "route": "direct",
            "final_report": refusal_message or "Frontier is designed for emerging markets investment analysis. I'm not able to help with that query — but feel free to ask me about any market, sector, or investment opportunity.",
            "errors": state.get("errors", [])
        }

    # ── In scope: extract structured intent ──
    intent_messages = [
        SystemMessage(content=f"""{FRONTIER_SYSTEM_PROMPT}{history_block}

Analyse the user's query and extract structured intent. Use the conversation history to resolve references like "this market", "the previous sector", "that country".
Respond with ONLY valid JSON — no markdown, no explanation:
{{
  "market": "Indonesia",
  "sector": "fintech / digital payments",
  "query_type": "single_market",
  "time_horizon": "medium_term",
  "investor_type": "fdi"
}}

market: specific country, or "Emerging Markets" if broad
sector: infer from context; "general" only as last resort
query_type: "single_market" | "market_comparison" | "risk_assessment" | "opportunity_scan"
time_horizon: "short_term" | "medium_term" (default) | "long_term"
investor_type: "fdi" | "portfolio" | "startup" | "general"
"""),
        HumanMessage(content=query)
    ]

    response = llm.invoke(intent_messages)
    content = clean_json(extract_text(response.content))

    try:
        parsed = json.loads(content)
        market        = parsed.get("market", "Emerging Markets")
        sector        = parsed.get("sector", "general")
        query_type    = parsed.get("query_type", "single_market")
        time_horizon  = parsed.get("time_horizon", "medium_term")
        investor_type = parsed.get("investor_type", "general")
    except Exception:
        market, sector = "Emerging Markets", "general"
        query_type, time_horizon, investor_type = "single_market", "medium_term", "general"

    print(f"    Market: {market} | Sector: {sector}")
    print(f"    Type: {query_type} | Horizon: {time_horizon} | Investor: {investor_type}")

    return {
        "market": market,
        "sector": sector,
        "query_type": query_type,
        "time_horizon": time_horizon,
        "investor_type": investor_type,
        "route": "full",
        "errors": state.get("errors", [])
    }


# ---------------------------------------------------------------------------
# NODE 2a: macro_node
# ---------------------------------------------------------------------------

def macro_node(state: AgentState) -> dict:
    print("[Node 2a] Collecting macro data...")
    market       = state.get("market", "Emerging Markets")
    time_horizon = state.get("time_horizon", "medium_term")
    horizon_map  = {
        "short_term":  "2025 economic outlook GDP inflation interest rates",
        "medium_term": "GDP growth forecast inflation economic stability 2025 2026",
        "long_term":   "long-term economic growth demographics infrastructure investment decade",
    }
    search_query = f"{market} {horizon_map.get(time_horizon, horizon_map['medium_term'])}"
    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live macro data for {market}")
        return {"macro_data": {"source": "tavily:live", "market": market, "live_search_results": live_data, "search_query": search_query}}
    else:
        macro_data = get_macro_indicators(market)
        print(f"    Stub fallback: GDP growth: {macro_data.get('gdp_growth_pct')}%")
        return {"macro_data": macro_data}


# ---------------------------------------------------------------------------
# NODE 2b: political_node
# ---------------------------------------------------------------------------

def political_node(state: AgentState) -> dict:
    print("[Node 2b] Scanning political risk...")
    market        = state.get("market", "Emerging Markets")
    investor_type = state.get("investor_type", "general")
    investor_map  = {
        "fdi":       "FDI policy foreign investment restrictions political stability governance",
        "portfolio": "capital controls currency risk political risk sovereign rating",
        "startup":   "startup ecosystem entrepreneurship policy government support",
        "general":   "political stability governance risk regulatory environment",
    }
    search_query = f"{market} {investor_map.get(investor_type, investor_map['general'])} 2025"
    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live political data for {market}")
        return {"political_data": {"source": "tavily:live", "market": market, "live_search_results": live_data, "search_query": search_query}}
    else:
        political_data = get_political_risk(market)
        print(f"    Stub fallback: Stability score: {political_data.get('political_stability_score')}/100")
        return {"political_data": political_data}


# ---------------------------------------------------------------------------
# NODE 2c: sector_node
# ---------------------------------------------------------------------------

def sector_node(state: AgentState) -> dict:
    print("[Node 2c] Analysing sector opportunity...")
    market     = state.get("market", "Emerging Markets")
    sector     = state.get("sector", "general")
    query_type = state.get("query_type", "single_market")
    qmap = {
        "market_comparison": f"best emerging markets {sector} investment opportunity comparison 2025",
        "risk_assessment":   f"{market} {sector} risks challenges barriers to entry 2025",
        "opportunity_scan":  f"top emerging markets {sector} growth opportunity whitespace 2025",
    }
    search_query = qmap.get(query_type, f"{market} {sector} market size growth opportunity 2025")
    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live sector data for {market} / {sector}")
        return {"sector_data": {"source": "tavily:live", "market": market, "sector": sector, "live_search_results": live_data, "search_query": search_query}}
    else:
        sector_data = get_sector_data(market, sector)
        print(f"    Stub fallback: {sector_data.get('sector')} | ${sector_data.get('market_size_usd_bn')}bn")
        return {"sector_data": sector_data}


# ---------------------------------------------------------------------------
# NODE 2d: exit_node  ← NEW
# Researches exit landscape, comparable deals, M&A and IPO activity
# ---------------------------------------------------------------------------

def exit_node(state: AgentState) -> dict:
    print("[Node 2d] Researching exit landscape & comparable deals...")
    market        = state.get("market", "Emerging Markets")
    sector        = state.get("sector", "general")
    investor_type = state.get("investor_type", "general")

    if investor_type == "portfolio":
        search_query = f"{market} {sector} IPO listings stock exchange liquidity exit 2024 2025"
    elif investor_type == "startup":
        search_query = f"{market} {sector} startup acquisition M&A venture exit deals 2024 2025"
    else:
        search_query = f"{market} {sector} M&A deals acquisitions exits comparable transactions 2024 2025"

    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live exit data for {market} / {sector}")
        return {"exit_data": {"source": "tavily:live", "market": market, "sector": sector, "live_search_results": live_data, "search_query": search_query}}
    else:
        print(f"    Exit data: no live results, using stub")
        return {"exit_data": {
            "source": "stub",
            "market": market,
            "sector": sector,
            "notes": "Limited exit data available. Market may be pre-liquidity stage.",
            "comparable_deals": [],
            "ipo_pipeline": "Nascent — limited public market infrastructure",
            "ma_activity": "Early stage — primarily strategic acquirers"
        }}


# ---------------------------------------------------------------------------
# NODE 2e: fx_node  ← NEW
# Researches currency risk, FX trends, capital controls
# ---------------------------------------------------------------------------

def fx_node(state: AgentState) -> dict:
    print("[Node 2e] Analysing currency & FX risk...")
    market = state.get("market", "Emerging Markets")

    search_query = f"{market} currency exchange rate trend capital controls USD 2025"
    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live FX data for {market}")
        return {"fx_data": {"source": "tavily:live", "market": market, "live_search_results": live_data, "search_query": search_query}}
    else:
        print(f"    FX data: no live results, using stub")
        return {"fx_data": {
            "source": "stub",
            "market": market,
            "currency": "Local currency",
            "usd_trend": "Stable",
            "volatility": "Medium",
            "capital_controls": "Some restrictions apply",
            "repatriation_risk": "Medium"
        }}


# ---------------------------------------------------------------------------
# NODE 2f: timing_node  ← NEW
# Researches market maturity, entry timing signal, sector cycle stage
# ---------------------------------------------------------------------------

def timing_node(state: AgentState) -> dict:
    print("[Node 2f] Assessing market timing & maturity...")
    market  = state.get("market", "Emerging Markets")
    sector  = state.get("sector", "general")

    search_query = f"{market} {sector} market maturity stage early growth saturation investment timing 2025"
    live_data = tavily_search(search_query, max_results=3)

    if live_data:
        print(f"    Tavily: live timing data for {market} / {sector}")
        return {"timing_data": {"source": "tavily:live", "market": market, "sector": sector, "live_search_results": live_data, "search_query": search_query}}
    else:
        print(f"    Timing data: no live results, using stub")
        return {"timing_data": {
            "source": "stub",
            "market": market,
            "sector": sector,
            "maturity_stage": "Growth",
            "entry_window": "Open",
            "cycle_position": "Mid-cycle",
            "notes": "Market showing growth-phase characteristics with expanding user base and increasing competition."
        }}


# ---------------------------------------------------------------------------
# NODE 3: aggregate_node
# ---------------------------------------------------------------------------

def aggregate_node(state: AgentState) -> dict:
    print("[Node 3] Aggregating research outputs...")
    errors = state.get("errors", [])
    for field, label in [
        ("macro_data", "macro"), ("political_data", "political"),
        ("sector_data", "sector"), ("exit_data", "exit"),
        ("fx_data", "fx"), ("timing_data", "timing")
    ]:
        if not state.get(field):
            errors.append(f"Warning: {label} data missing")
    print(f"    All research collected. Errors so far: {len(errors)}")
    return {"errors": errors}


# ---------------------------------------------------------------------------
# NODE 4: regulatory_node
# ---------------------------------------------------------------------------

def regulatory_node(state: AgentState) -> dict:
    print("[Node 4] Checking regulatory environment...")
    market        = state.get("market", "Emerging Markets")
    sector        = state.get("sector", "general")
    investor_type = state.get("investor_type", "general")

    if investor_type == "fdi":
        search_query = f"{market} {sector} FDI rules foreign ownership limits licensing requirements 2025"
    elif investor_type == "startup":
        search_query = f"{market} {sector} startup registration licensing fintech sandbox regulations 2025"
    else:
        search_query = f"{market} {sector} regulation compliance requirements market entry rules 2025"

    live_data = tavily_search(search_query, max_results=2)

    if live_data:
        print(f"    Tavily: live regulatory data for {market}")
        return {"regulatory_data": {"source": "tavily:live", "market": market, "sector": sector, "live_search_results": live_data, "search_query": search_query}}
    else:
        regulatory_data = get_regulatory_environment(market, sector)
        print(f"    Stub fallback: {regulatory_data.get('primary_regulator', 'unknown')[:50]}...")
        return {"regulatory_data": regulatory_data}


# ---------------------------------------------------------------------------
# NODE 5: brief_node
# Now includes exit, FX, and timing context in the report + chart data
# ---------------------------------------------------------------------------

def brief_node(state: AgentState) -> dict:
    print("[Node 5] Writing draft market entry brief...")
    llm = get_llm()

    market        = state.get("market", "Unknown")
    sector        = state.get("sector", "Unknown")
    query_type    = state.get("query_type", "single_market")
    time_horizon  = state.get("time_horizon", "medium_term")
    investor_type = state.get("investor_type", "general")
    query         = state.get("query", "")

    def fmt(d):
        if isinstance(d, dict) and d.get("source") == "tavily:live":
            return f"[Live search: '{d.get('search_query', '')}']\n\n{d.get('live_search_results', '')}"
        return json.dumps(d, indent=2)

    context = f"""
ORIGINAL QUERY: {query}
MARKET: {market} | SECTOR: {sector}
QUERY TYPE: {query_type} | TIME HORIZON: {time_horizon} | INVESTOR TYPE: {investor_type}

=== MACROECONOMIC DATA ===
{fmt(state.get("macro_data", {}))}

=== POLITICAL RISK DATA ===
{fmt(state.get("political_data", {}))}

=== SECTOR DATA ===
{fmt(state.get("sector_data", {}))}

=== REGULATORY DATA ===
{fmt(state.get("regulatory_data", {}))}

=== EXIT LANDSCAPE & COMPARABLE DEALS ===
{fmt(state.get("exit_data", {}))}

=== CURRENCY & FX RISK ===
{fmt(state.get("fx_data", {}))}

=== MARKET TIMING & MATURITY ===
{fmt(state.get("timing_data", {}))}
"""

    investor_guidance = {
        "fdi":       "Focus on operational considerations: local partnerships, ownership structures, workforce, supply chain, and regulatory compliance timelines.",
        "portfolio": "Focus on return profile, valuation benchmarks, exit liquidity, currency hedging, and sovereign risk.",
        "startup":   "Focus on product-market fit signals, local competition, talent availability, funding ecosystem, and regulatory sandbox opportunities.",
        "general":   "Provide a balanced overview suitable for a strategic decision-maker.",
    }

    structure_note = {
        "market_comparison": "Produce a ranked comparison of the top 3-5 markets. Use a comparison table. End with a clear #1 recommendation.",
        "risk_assessment":   "Lead with risk analysis. Be direct about red flags. Risk Assessment should be most detailed.",
        "opportunity_scan":  "Lead with opportunity size. Identify attractive whitespace. Be concrete about entry vectors.",
    }.get(query_type, "This is a single-market deep dive. Be specific and data-driven throughout.")

    report_messages = [
        SystemMessage(content=f"""{FRONTIER_SYSTEM_PROMPT}

Write a concise but comprehensive market entry brief using the research data provided.

INVESTOR LENS: {investor_guidance.get(investor_type, investor_guidance['general'])}
STRUCTURE GUIDANCE: {structure_note}

Use exactly these markdown headers:

# Market Entry Brief: [{market}] — [{sector}]

## Executive Summary
2-3 sentences. Opportunity size + overall verdict.

## Macroeconomic Context
Key economic factors with specific numbers. Flag tailwinds and headwinds for the {time_horizon.replace("_", "-")} horizon.

## Sector Opportunity
Market size, growth rate, key players, and where the whitespace is.

## Exit Landscape & Comparable Deals
Recent M&A activity, IPO pipeline, comparable transactions and implied valuations. Is there a clear exit path?

## Currency & FX Risk
Currency trend, volatility, capital controls, repatriation risk, and hedging considerations.

## Market Timing
Where is this market on the maturity curve? Is now the right moment to enter — early mover, growth phase, or late/saturated?

## Risk Assessment
| Risk Factor | Rating | Commentary |
|---|---|---|
Rows: Political Stability, Currency Risk, Regulatory Risk, Competitive Intensity, Infrastructure, Exit Liquidity
Ratings: Low / Medium / High

## Regulatory Landscape
Licences needed, timeline, key restrictions, red flags for a {investor_type} investor.

## Recommendation
**Verdict: [PROCEED / PROCEED WITH CAUTION / HIGH RISK — HOLD]**
3-4 sentences. Specific and actionable.

Be sharp. Cite data. Avoid vague generalities."""),
        HumanMessage(content=f"Write the market entry brief:\n{context}")
    ]

    report_response = llm.invoke(report_messages)
    draft_report = extract_text(report_response.content)
    print("    Draft report written.")

    # Chart data — now includes fx_trend and timing/maturity
    chart_messages = [
        SystemMessage(content="""You are a data analyst. Extract key data for visualisation.
Respond with ONLY valid JSON — no markdown, no backticks, no explanation.

{
  "risk_chart": {
    "title": "Risk Assessment",
    "labels": ["Political Stability", "Currency Risk", "Regulatory Risk", "Competitive Intensity", "Infrastructure", "Exit Liquidity"],
    "scores": [65, 45, 70, 80, 40, 55],
    "comment": "Scores 0-100. Higher = higher risk."
  },
  "market_size_chart": {
    "title": "Market Size (USD bn)",
    "markets": ["Market A", "Market B"],
    "values": [2.5, 4.1]
  },
  "gdp_chart": {
    "title": "GDP Growth Rate (%)",
    "markets": ["Market A", "Market B"],
    "values": [5.1, 6.4]
  },
  "fx_chart": {
    "title": "Currency Risk Factors",
    "labels": ["Volatility", "Capital Controls", "Repatriation Risk", "USD Correlation", "Inflation Risk"],
    "scores": [40, 30, 45, 60, 55],
    "comment": "Scores 0-100. Higher = higher risk."
  },
  "timing_chart": {
    "market": "Indonesia",
    "sector": "fintech",
    "maturity_stage": "Growth",
    "stage_index": 2,
    "stages": ["Nascent", "Early", "Growth", "Mature", "Saturated"],
    "entry_signal": "STRONG BUY",
    "entry_rationale": "Market is in high-growth phase with expanding user base and limited saturation.",
    "comparable_deals": [
      {"name": "Deal / Company A", "amount": "$45M", "year": "2024", "type": "Series B"},
      {"name": "Deal / Company B", "amount": "$120M", "year": "2023", "type": "Acquisition"}
    ]
  }
}

Rules:
- All scores must be integers 0-100
- All values must be numbers
- stage_index: 0=Nascent, 1=Early, 2=Growth, 3=Mature, 4=Saturated
- entry_signal: one of "STRONG BUY" | "BUY" | "HOLD" | "WAIT" | "AVOID"
- Use real data from research where available
- comparable_deals: include up to 4 real recent deals if found in the research, else leave as empty array []
- Keep market names short"""),
        HumanMessage(content=f"Extract chart data:\n{context}")
    ]

    chart_data = None
    try:
        chart_response = llm.invoke(chart_messages)
        chart_raw = clean_json(extract_text(chart_response.content))
        chart_data = json.loads(chart_raw)
        print("    Chart data generated.")
    except Exception as e:
        print(f"    Chart data generation failed: {e}")

    return {"draft_report": draft_report, "chart_data": chart_data}


# ---------------------------------------------------------------------------
# NODE 6: reflect_node
# ---------------------------------------------------------------------------

def reflect_node(state: AgentState) -> dict:
    print("[Node 6] Reflecting on draft report...")
    llm = get_llm()

    draft         = state.get("draft_report", "")
    query         = state.get("query", "")
    market        = state.get("market", "")
    investor_type = state.get("investor_type", "general")
    query_type    = state.get("query_type", "single_market")

    def fmt_short(d):
        if isinstance(d, dict) and d.get("source") == "tavily:live":
            return f"[Live: '{d.get('search_query', '')}']\n{d.get('live_search_results', '')[:600]}"
        return json.dumps(d, indent=2)[:600]

    research_summary = f"""
MACRO: {fmt_short(state.get('macro_data', {}))}
POLITICAL: {fmt_short(state.get('political_data', {}))}
SECTOR: {fmt_short(state.get('sector_data', {}))}
REGULATORY: {fmt_short(state.get('regulatory_data', {}))}
EXIT: {fmt_short(state.get('exit_data', {}))}
FX: {fmt_short(state.get('fx_data', {}))}
TIMING: {fmt_short(state.get('timing_data', {}))}
"""

    critique_messages = [
        SystemMessage(content=f"""{FRONTIER_SYSTEM_PROMPT}

You are acting as a critical editor reviewing a market entry brief written by a junior analyst.
Identify weaknesses. Evaluate:
1. Are claims backed by specific data, or vague generalities?
2. Is the exit landscape section concrete — are there real deals cited?
3. Does the FX section give actionable hedging guidance?
4. Is the timing signal justified by evidence — not just asserted?
5. Is the recommendation clearly justified by the evidence?
6. Is the investor lens consistently applied throughout?

Respond with 5-8 bullet points. Be direct and specific. Flag exactly which sections need strengthening."""),
        HumanMessage(content=f"QUERY: {query}\nINVESTOR TYPE: {investor_type}\nQUERY TYPE: {query_type}\n\nDRAFT:\n{draft}\n\nRESEARCH:\n{research_summary}")
    ]

    critique_response = llm.invoke(critique_messages)
    reflection_notes = extract_text(critique_response.content)
    print("    Critique generated.")

    rewrite_messages = [
        SystemMessage(content=f"""{FRONTIER_SYSTEM_PROMPT}

You are rewriting a market entry brief after receiving a critique.
You have a draft and a critique. Produce an improved final version addressing every critique point.
Keep the same markdown structure. Make it sharper, more specific, better evidenced.
Do not mention the critique process — just deliver the improved report."""),
        HumanMessage(content=f"QUERY: {query}\n\nDRAFT:\n{draft}\n\nCRITIQUE:\n{reflection_notes}\n\nRESEARCH:\n{research_summary}\n\nWrite the improved final report:")
    ]

    rewrite_response = llm.invoke(rewrite_messages)
    final_report = extract_text(rewrite_response.content)
    print("    Final report written after reflection.")

    return {"reflection_notes": reflection_notes, "final_report": final_report}
