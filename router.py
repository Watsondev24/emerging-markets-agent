# router.py
# Classifies incoming queries BEFORE the full pipeline runs.
# Returns either a direct Gemini answer or routes to the full agent graph.

import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.2,
    )


def clean_json(raw: str) -> str:
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", str(content))
    if isinstance(content, list):
        return "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)


# ---------------------------------------------------------------------------
# STEP 1: Classify the query
# ---------------------------------------------------------------------------

def classify_query(query: str, history: str = "") -> dict:
    llm = get_llm()
    history_block = f"\n\nCONVERSATION HISTORY:\n{history}" if history else ""

    messages = [
        SystemMessage(content=f"""You are a routing assistant for Frontier, an institutional emerging markets investment intelligence platform.{history_block}

Classify the user's query into one of THREE routes:

"out_of_scope" — Nothing to do with markets, investment, economics, finance, geopolitics, or business:
  - Recipes, cooking, food ("how do I bake a cake")
  - Sports scores, entertainment, celebrities
  - Personal advice, health, relationships
  - General trivia unrelated to finance or economics
  NOTE: If the conversation history shows a finance topic was being discussed, follow-up phrases like "show me more", "what about X", "summarise this", "show me visuals" are IN scope — use "direct".

"direct" — Finance/markets related, answerable from general knowledge. Also use for follow-up requests on prior conversation:
  - Definitions ("What is fintech?", "What does GDP mean?")
  - Conceptual questions ("What's the difference between FDI and portfolio investment?")
  - Historical facts ("When did Indonesia join ASEAN?")
  - How-to investing concepts ("How does currency hedging work?")
  - Follow-ups referencing prior answers ("show me visuals for this", "summarise that", "explain further")

"pipeline" — Requires live research, real data, and multi-step analysis:
  - Market entry analysis ("Should I expand into Nigeria?")
  - Investment opportunity assessment
  - Risk assessments for specific markets
  - Sector-specific opportunity analysis
  - Anything asking for a current recommendation, verdict, or live data

Respond with ONLY valid JSON:
{{
  "route": "direct",
  "reason": "Short reason here",
  "query_type": "definition"
}}

query_type options: "definition", "general_knowledge", "conceptual", "market_analysis", "risk_assessment", "opportunity_scan", "market_comparison", "out_of_scope"
"""),
        HumanMessage(content=query)
    ]

    response = llm.invoke(messages)
    content = clean_json(extract_text(response.content))

    try:
        result = json.loads(content)
        route = result.get("route", "pipeline")
        reason = result.get("reason", "")
        query_type = result.get("query_type", "market_analysis")
    except Exception:
        route = "pipeline"
        reason = "Could not classify query, defaulting to full analysis"
        query_type = "market_analysis"

    print(f"[Router] Route: {route} | Type: {query_type} | Reason: {reason[:60]}")
    return {"route": route, "reason": reason, "query_type": query_type}


# ---------------------------------------------------------------------------
# STEP 2: Direct answer (no pipeline)
# ---------------------------------------------------------------------------

def direct_answer(query: str, query_type: str, history: str = "") -> str:
    llm = get_llm()

    if query_type == "out_of_scope":
        return "Frontier is an emerging markets investment intelligence platform. I'm not able to help with that — but feel free to ask me about any market, sector, investment opportunity, or economic trend."

    history_block = f"\n\nCONVERSATION HISTORY (use this to understand follow-up questions):\n{history}" if history else ""

    type_guidance = {
        "definition": "Give a clear, concise definition with a practical example. Keep it under 200 words.",
        "general_knowledge": "Answer factually and concisely. Include key context relevant to emerging markets investing.",
        "conceptual": "Explain the concept clearly with a practical example relevant to emerging markets investing.",
    }.get(query_type, "Answer clearly and helpfully. Be concise but complete. If this is a follow-up, reference the prior context.")

    messages = [
        SystemMessage(content=f"""You are a senior emerging markets investment analyst at Frontier Intelligence.
Your sole expertise is markets, finance, economics, investment strategy, and geopolitics.{history_block}

Answer the user's question from your knowledge. If it's a follow-up, use the conversation history to understand what they're referring to.

{type_guidance}

Format your response in clean markdown. Use headers sparingly.
If the question is completely unrelated to finance, economics, or markets — respond only with:
"Frontier is an emerging markets investment intelligence platform. I'm not able to help with that — but feel free to ask me about any market, sector, or investment opportunity." """),
        HumanMessage(content=query)
    ]

    response = llm.invoke(messages)
    return extract_text(response.content)
