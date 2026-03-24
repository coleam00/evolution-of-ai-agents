"""Validate skill structure and content."""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.skill_loader import SkillLoader
from src.settings import load_settings

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)


def validate_skill_structure(skill_dir: Path) -> list[str]:
    """Validate skill directory structure."""
    issues = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        issues.append("Missing SKILL.md")
        return issues

    # Check for frontmatter
    content = skill_md.read_text()
    if not content.startswith("---"):
        issues.append("SKILL.md missing YAML frontmatter")

    # Check for optional directories
    if (skill_dir / "references").exists():
        ref_files = list((skill_dir / "references").glob("*.md"))
        if not ref_files:
            issues.append("references/ directory exists but is empty")

    if (skill_dir / "scripts").exists():
        script_files = list((skill_dir / "scripts").glob("*.py"))
        if not script_files:
            issues.append("scripts/ directory exists but is empty")

    return issues


def main():
    """Validate all skills."""
    console.print(Panel(
        "[bold blue]Skill Validation Report[/bold blue]",
        style="blue"
    ))

    settings = load_settings()
    loader = SkillLoader(settings.skills_dir)
    skills = loader.discover_skills()

    console.print(f"\n[cyan]Found {len(skills)} skill(s)[/cyan]\n")

    # Create table
    table = Table(title="Skill Validation Results")
    table.add_column("Skill", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Issues", style="yellow")

    all_valid = True

    for skill in skills:
        issues = validate_skill_structure(skill.skill_path)

        if issues:
            all_valid = False
            status = "[red]FAIL[/red]"
            issues_str = "\n".join(f"  - {i}" for i in issues)
        else:
            status = "[green]PASS[/green]"
            issues_str = "None"

        table.add_row(skill.name, status, issues_str)

    console.print(table)

    if all_valid:
        console.print("\n[bold green]All skills valid![/bold green]")
        return 0
    else:
        console.print("\n[bold red]Some skills have issues[/bold red]")
        return 1


if __name__ == '__main__':
    exit(main())
