# main.py
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from graph import build_graph
from state import AgentState

load_dotenv()

console = Console()

EXAMPLE_QUERIES = [
    "Should we expand our payments platform into Indonesia?",
    "What is the renewable energy investment opportunity in Vietnam?",
    "Assess the e-commerce market in Nigeria",
    "We are considering entering the telecoms tower market in Ghana",
    "Evaluate the SME lending opportunity in Bangladesh",
]


def extract_report(report):
    """Handle cases where the report comes back as a dict or string."""
    if isinstance(report, str):
        return report
    if isinstance(report, dict):
        return report.get("text", str(report))
    if isinstance(report, list):
        parts = []
        for item in report:
            if isinstance(item, dict):
                parts.append(item.get("text", str(item)))
            else:
                parts.append(str(item))
        return " ".join(parts)
    return str(report)


def run_agent(query: str) -> str:
    agent = build_graph()

    initial_state: AgentState = {
        "query": query,
        "market": "",
        "sector": "",
        "macro_data": None,
        "political_data": None,
        "sector_data": None,
        "regulatory_data": None,
        "final_report": None,
        "errors": [],
    }

    console.print("\n[bold green]Running agent pipeline...[/bold green]")
    console.print("─" * 60)

    result = agent.invoke(initial_state)

    report = result.get("final_report", "No report generated.")
    return extract_report(report)


def main():
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY not found in .env file")
        return

    console.print(Panel.fit(
        "[bold green]Emerging Markets Intelligence Agent[/bold green]\n"
        "[dim]Powered by LangGraph + Gemini[/dim]",
        border_style="green"
    ))

    console.print("\n[dim]Example queries:[/dim]")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        console.print(f"  [dim]{i}.[/dim] {q}")

    console.print("\n[dim]Type 'quit' to exit. Type a number (1-5) to use an example query.[/dim]\n")

    while True:
        query = Prompt.ask("[bold green]Your query[/bold green]")

        if query.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye.[/dim]")
            break

        if query.strip() in ("1", "2", "3", "4", "5"):
            query = EXAMPLE_QUERIES[int(query.strip()) - 1]
            console.print(f"[dim]Using: {query}[/dim]")

        if not query.strip():
            continue

        try:
            report = run_agent(query)
            console.print("\n" + "─" * 60)
            console.print(Markdown(report))
            console.print("─" * 60 + "\n")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print("[dim]Check your API keys and internet connection.[/dim]")


if __name__ == "__main__":
    main()
