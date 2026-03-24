#!/usr/bin/env python3
"""Conversational CLI with real-time streaming and tool call visibility."""

import asyncio
import sys
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from pydantic_ai import Agent
from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPartDelta
from dotenv import load_dotenv

from src.agent import skill_agent
from src.dependencies import AgentDependencies
from src.settings import load_settings

# Load environment variables
load_dotenv(override=True)

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)


async def stream_agent_interaction(
    user_input: str,
    message_history: List,
    agent,
    deps: AgentDependencies = None
) -> tuple[str, List]:
    """
    Stream agent interaction with real-time tool call display.

    Args:
        user_input: The user's input text
        message_history: List of ModelRequest/ModelResponse objects for conversation context
        agent: The Pydantic AI agent
        deps: Agent dependencies (skill loader, settings, etc.)

    Returns:
        Tuple of (streamed_text, updated_message_history)
    """
    try:
        return await _stream_agent(user_input, agent, message_history, deps)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return ("", [])


async def _stream_agent(
    user_input: str,
    agent,
    message_history: List,
    deps: AgentDependencies = None
) -> tuple[str, List]:
    """Stream the agent execution and return response."""

    response_text = ""

    # Create deps if not provided
    if deps is None:
        deps = AgentDependencies()

    # Stream the agent execution with message history and deps
    async with agent.iter(
        user_input,
        message_history=message_history,
        deps=deps
    ) as run:

        async for node in run:

            # Handle user prompt node
            if Agent.is_user_prompt_node(node):
                pass  # Clean start

            # Handle model request node - stream the thinking process
            elif Agent.is_model_request_node(node):
                # Show assistant prefix at the start
                console.print("[bold blue]Assistant:[/bold blue] ", end="")

                # Stream model request events for real-time text
                async with node.stream(run.ctx) as request_stream:
                    async for event in request_stream:
                        # Handle text part start events
                        if isinstance(event, PartStartEvent) and event.part.part_kind == 'text':
                            initial_text = event.part.content
                            if initial_text:
                                console.print(initial_text, end="")
                                response_text += initial_text

                        # Handle text delta events for streaming
                        elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                            delta_text = event.delta.content_delta
                            if delta_text:
                                console.print(delta_text, end="")
                                response_text += delta_text

                # New line after streaming completes
                console.print()

            # Handle tool calls
            elif Agent.is_call_tools_node(node):
                # Stream tool execution events
                async with node.stream(run.ctx) as tool_stream:
                    async for event in tool_stream:
                        event_type = type(event).__name__

                        if event_type == "FunctionToolCallEvent":
                            # Extract tool name from the event
                            tool_name = "Unknown Tool"
                            args = None

                            # Check if the part attribute contains the tool call
                            if hasattr(event, 'part'):
                                part = event.part

                                # Check for tool name
                                if hasattr(part, 'tool_name'):
                                    tool_name = part.tool_name
                                elif hasattr(part, 'function_name'):
                                    tool_name = part.function_name
                                elif hasattr(part, 'name'):
                                    tool_name = part.name

                                # Check for arguments
                                if hasattr(part, 'args'):
                                    args = part.args
                                elif hasattr(part, 'arguments'):
                                    args = part.arguments

                            console.print(f"  [cyan]Calling tool:[/cyan] [bold]{tool_name}[/bold]")

                            # Show skill-specific arguments
                            if args and isinstance(args, dict):
                                if 'skill_name' in args:
                                    console.print(f"    [dim]Skill:[/dim] {args['skill_name']}")
                                if 'file_path' in args:
                                    console.print(f"    [dim]File:[/dim] {args['file_path']}")
                                if 'directory' in args:
                                    console.print(f"    [dim]Directory:[/dim] {args['directory']}")
                            elif args:
                                args_str = str(args)
                                if len(args_str) > 100:
                                    args_str = args_str[:97] + "..."
                                console.print(f"    [dim]Args: {args_str}[/dim]")

                        elif event_type == "FunctionToolResultEvent":
                            console.print(f"  [green]Tool execution completed[/green]")

            # Handle end node
            elif Agent.is_end_node(node):
                pass

    # Get new messages from this run to add to history
    new_messages = run.result.new_messages()

    # Get final output
    final_output = run.result.output if hasattr(run.result, 'output') else str(run.result)
    response = response_text.strip() or final_output

    # Return both streamed text and new messages
    return (response, new_messages)


def display_welcome():
    """Display welcome message with configuration info."""
    settings = load_settings()

    welcome = Panel(
        "[bold blue]Skill-Based AI Agent[/bold blue]\n\n"
        "[green]Intelligent agent with progressive disclosure skills[/green]\n"
        f"[dim]LLM: {settings.llm_model}[/dim]\n"
        f"[dim]Skills Directory: {settings.skills_dir}[/dim]\n\n"
        "[dim]Type 'exit' to quit, 'info' for system info, 'clear' to clear screen[/dim]",
        style="blue",
        padding=(1, 2)
    )
    console.print(welcome)
    console.print()


async def main():
    """Main conversation loop."""

    # Show welcome
    display_welcome()

    # Initialize dependencies (reused across all interactions)
    deps = AgentDependencies()
    await deps.initialize()

    # Show discovered skills
    if deps.skill_loader and deps.skill_loader.skills:
        skills_list = ", ".join(deps.skill_loader.skills.keys())
        console.print(f"[bold green]OK[/bold green] Agent initialized with skills: {skills_list}\n")
    else:
        console.print("[bold green]OK[/bold green] Agent initialized (no skills found)\n")

    # Initialize message history
    message_history = []

    try:
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold green]You").strip()

                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[yellow]Goodbye![/yellow]")
                    break

                elif user_input.lower() == 'info':
                    settings = load_settings()
                    skills_info = "None"
                    if deps.skill_loader and deps.skill_loader.skills:
                        skills_info = ", ".join(deps.skill_loader.skills.keys())
                    console.print(Panel(
                        f"[cyan]LLM Provider:[/cyan] {settings.llm_provider}\n"
                        f"[cyan]LLM Model:[/cyan] {settings.llm_model}\n"
                        f"[cyan]Skills Directory:[/cyan] {settings.skills_dir}\n"
                        f"[cyan]Loaded Skills:[/cyan] {skills_info}",
                        title="System Configuration",
                        border_style="magenta"
                    ))
                    continue

                elif user_input.lower() == 'clear':
                    console.clear()
                    display_welcome()
                    continue

                if not user_input:
                    continue

                # Stream the interaction and get response (pass deps)
                response_text, new_messages = await stream_agent_interaction(
                    user_input,
                    message_history,
                    skill_agent,
                    deps
                )

                # Add new messages to history
                message_history.extend(new_messages)

                # Add spacing after response
                console.print()

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                import traceback
                traceback.print_exc()
                continue

    finally:
        console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    asyncio.run(main())
