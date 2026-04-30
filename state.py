# state.py
from typing import TypedDict, Optional


class AgentState(TypedDict):
    # --- Input ---
    query: str
    conversation_history: str  # formatted prior turns for context

    # --- Parsed intent (filled by parse_query node) ---
    market: str
    sector: str
    query_type: str
    time_horizon: str
    investor_type: str
    route: str

    # --- Research outputs ---
    macro_data: Optional[dict]
    political_data: Optional[dict]
    sector_data: Optional[dict]
    regulatory_data: Optional[dict]
    exit_data: Optional[dict]
    fx_data: Optional[dict]
    timing_data: Optional[dict]

    # --- Report stages ---
    draft_report: Optional[str]
    reflection_notes: Optional[str]
    final_report: Optional[str]
    chart_data: Optional[dict]

    # --- Internal bookkeeping ---
    errors: list[str]
