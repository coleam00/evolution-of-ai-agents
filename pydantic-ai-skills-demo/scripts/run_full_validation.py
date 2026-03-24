"""Run complete validation pipeline: tests -> evals -> skill validation -> agent tests."""

import sys
import subprocess
from rich.console import Console
from rich.panel import Panel

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and report results."""
    console.print(f"\n[bold cyan]Running:[/bold cyan] {description}")
    console.print(f"[dim]Command: {' '.join(cmd)}[/dim]\n")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        console.print(f"[green]PASS: {description}[/green]")
        return True
    else:
        console.print(f"[red]FAIL: {description}[/red]")
        return False


def main():
    """Run full validation pipeline."""
    console.print(Panel(
        "[bold blue]Full Validation Pipeline[/bold blue]\n\n"
        "Running: Unit Tests → Integration Tests → Evals → Skill Validation → Agent Tests",
        style="blue",
        padding=(1, 2)
    ))

    steps = [
        (["uv", "run", "pytest", "tests/test_skill_loader.py", "-v"], "Unit Tests: Skill Loader"),
        (["uv", "run", "pytest", "tests/test_skill_tools.py", "-v"], "Unit Tests: Skill Tools"),
        (["uv", "run", "pytest", "tests/test_agent.py", "-v"], "Integration Tests: Agent"),
        (["uv", "run", "python", "-m", "scripts.validate_skills"], "Skill Validation"),
        (["uv", "run", "python", "-m", "tests.evals.run_evals"], "Evaluation Suite"),
    ]

    results = []

    for cmd, desc in steps:
        success = run_command(cmd, desc)
        results.append((desc, success))

    # Summary
    console.print(f"\n{'='*60}")
    console.print("[bold]VALIDATION SUMMARY[/bold]")
    console.print(f"{'='*60}\n")

    all_passed = True
    for desc, success in results:
        status = "[green]PASS[/green]" if success else "[red]FAIL[/red]"
        console.print(f"{status} {desc}")
        if not success:
            all_passed = False

    console.print()

    if all_passed:
        console.print("[bold green]All validation steps passed![/bold green]")
        return 0
    else:
        console.print("[bold red]Some validation steps failed[/bold red]")
        return 1


if __name__ == '__main__':
    sys.exit(main())
