import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import build_graph
from state import AgentState
from router import classify_query, direct_answer
# from ibm_watsonx_orchestrate.client.chat.run_client import RunClient
# from ibm_watsonx_orchestrate.client.threads.threads_client import ThreadsClient

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WXO_API_KEY = os.getenv("WXO_API_KEY")
WXO_URL = os.getenv("WXO_URL")
WXO_AGENT_ID = "446cb76b-ed0c-49e7-90d2-11f134ab7c84"

class QueryRequest(BaseModel):
    query: str
    conversation_history: list = []

def extract_report(r):
    if isinstance(r, str): return r
    if isinstance(r, dict): return r.get("text", str(r))
    if isinstance(r, list): return "\n".join([i.get("text", str(i)) if isinstance(i, dict) else str(i) for i in r])
    return str(r)

def format_history(history: list) -> str:
    """Format conversation history as a readable string for context injection."""
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:  # last 3 turns (6 messages)
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")[:400]  # truncate long responses
        lines.append(f"{role}: {content}")
    return "\n".join(lines)

async def get_iam_token(api_key):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key})
        if r.status_code != 200: raise HTTPException(401, f"IAM failed: {r.text}")
        return r.json()["access_token"]

@app.post("/analyse")
async def analyse(request: QueryRequest):
    history_str = format_history(request.conversation_history)

    # ── Step 1: Route the query ──
    routing = classify_query(request.query, history_str)

    # ── Step 2a: Direct answer or out of scope — skip the pipeline entirely ──
    if routing["route"] in ("direct", "out_of_scope"):
        print(f"[API] Direct answer route — skipping pipeline")
        answer = direct_answer(request.query, routing.get("query_type", "general_knowledge"), history_str)
        return {
            "report":           answer,
            "draft_report":     "",
            "reflection_notes": "",
            "chart_data":       None,
            "market":           "",
            "sector":           "",
            "query_type":       routing.get("query_type", "general_knowledge"),
            "investor_type":    "",
            "time_horizon":     "",
            "errors":           [],
            "agent":            "askmarketiq",
            "route":            routing["route"],
            "route_reason":     routing.get("reason", "")
        }

    # ── Step 2b: Full pipeline ──
    print(f"[API] Full pipeline route")
    agent = build_graph()
    state: AgentState = {
        "query": request.query,
        "conversation_history": history_str,
        "market": "", "sector": "",
        "query_type": "", "time_horizon": "", "investor_type": "",
        "macro_data": None, "political_data": None, "sector_data": None,
        "regulatory_data": None, "exit_data": None, "fx_data": None, "timing_data": None,
        "draft_report": None, "reflection_notes": None,
        "final_report": None, "chart_data": None, "errors": []
    }
    result = agent.invoke(state)
    return {
        "report":           extract_report(result.get("final_report", "")),
        "draft_report":     extract_report(result.get("draft_report", "")),
        "reflection_notes": extract_report(result.get("reflection_notes", "")),
        "chart_data":       result.get("chart_data"),
        "market":           result.get("market", ""),
        "sector":           result.get("sector", ""),
        "query_type":       result.get("query_type", ""),
        "investor_type":    result.get("investor_type", ""),
        "time_horizon":     result.get("time_horizon", ""),
        "errors":           result.get("errors", []),
        "agent":            "askmarketiq",
        "route":            "pipeline",
        "route_reason":     ""
    }

# @app.post("/analyse-wxo")
# async def analyse_wxo(request: QueryRequest):
#     ...

@app.get("/health")
async def health(): return {"status": "ok"}
