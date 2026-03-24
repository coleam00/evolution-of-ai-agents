"""Interactive script to test agent with different skill scenarios."""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from src.agent import skill_agent
from src.dependencies import AgentDependencies

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)

# Predefined test queries
TEST_QUERIES = {
    "weather": [
        "What's the weather in New York?",
        "What's the forecast for London?",
        "How hot is it in Tokyo?",
    ],
    "code_review": [
        "Review this code: def add(a, b): return a + b",
        "Check this for security issues: user_input = request.GET['name']",
        "Review this authentication function for best practices",
    ],
    "mixed": [
        "What's the weather in Paris and review this code: def hello(): pass",
    ]
}


async def test_query(query: str, deps: AgentDependencies):
    """Test a single query and display results."""
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")
    console.print("[dim]Running agent...[/dim]\n")

    try:
        result = await skill_agent.run(query, deps=deps)

        console.print(Panel(
            result.output,
            title="[green]Response[/green]",
            border_style="green"
        ))

        return True
    except Exception as e:
        console.print(Panel(
            str(e),
            title="[red]Error[/red]",
            border_style="red"
        ))
        return False


async def main():
    """Run interactive agent tests."""
    console.print(Panel(
        "[bold blue]Skill-Based Agent Testing[/bold blue]\n\n"
        "This script runs predefined queries to test skill loading.",
        style="blue"
    ))

    # Initialize dependencies once
    deps = AgentDependencies()
    await deps.initialize()

    console.print(f"\n[bold green]OK[/bold green] Agent initialized with skills: {', '.join(deps.skill_loader.skills.keys())}\n")

    # Test weather queries
    console.print("[bold]Testing Weather Skill[/bold]")
    console.print("="*60)
    for query in TEST_QUERIES["weather"]:
        await test_query(query, deps)
        await asyncio.sleep(0.5)  # Brief pause between queries

    # Test code review queries
    console.print("\n[bold]Testing Code Review Skill[/bold]")
    console.print("="*60)
    for query in TEST_QUERIES["code_review"]:
        await test_query(query, deps)
        await asyncio.sleep(0.5)

    console.print("\n[bold green]Testing complete![/bold green]")


if __name__ == '__main__':
    asyncio.run(main())
