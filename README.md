# How Building AI Agents Has Completely Changed

Three working examples showing how AI agent development has evolved - from the traditional RAG-based approach to modern batteries-included SDKs and skill-based frameworks.

## The Evolution

| Era | Approach | Example |
|-----|----------|---------|
| **2024-2025** | Chunk docs, embed, vector search, wire the agent loop yourself | `rag-agent-demo/` |
| **2026 (SDKs)** | Built-in tools + custom MCP servers, no glue code | `claude-agent-sdk-demo/` |
| **2026 (Frameworks)** | Type-safe agents with progressive skill disclosure | `pydantic-ai-skills-demo/` |

## Examples

### `rag-agent-demo/` - The Traditional Approach (Python)

The classic RAG pattern that was the default playbook for building AI agents. Shows the full pipeline: chunk documents, generate embeddings, store in a vector database, retrieve relevant chunks, feed to an LLM.

```bash
cd rag-agent-demo
cp .env.example .env     # Add your OpenAI key + database URL
docker compose up -d     # Start PostgreSQL with pgvector
uv sync
uv run python -m ingestion.ingest --documents documents/ --clean
uv run python cli.py
```

**Stack:** Pydantic AI + PostgreSQL/pgvector + OpenAI embeddings

This works - and it's still the right call when you have large document corpora. But for many use cases, the newer approaches below eliminate the need for this infrastructure entirely.

### `claude-agent-sdk-demo/` - Batteries-Included SDK (TypeScript)

A research agent that comes with tools out of the box. No RAG pipeline, no vector database, no embedding infrastructure. The SDK provides Read, Write, WebSearch, Bash, and Grep as built-in tools, and you can add your own via MCP servers.

```bash
cd claude-agent-sdk-demo
bun install
bun run agent.ts "How AI agent frameworks evolved in 2026"
```

**What this demonstrates:**
- **Built-in tools** - Read, Write, WebSearch, Bash, Grep with zero setup
- **Custom MCP server** - `createSdkMcpServer()` with `save_note` and `search_notes` tools
- **Subagents** - Researcher and Writer agents that the orchestrator delegates to
- **Hooks** - Real-time monitoring of tool usage

Uses your local Claude Code CLI credentials - no API key needed.

### `pydantic-ai-skills-demo/` - Framework with Skills (Python)

A Pydantic AI agent with a skill system implementing progressive disclosure. Instead of loading all instructions upfront, skills are discovered at ~100 tokens each and loaded on demand - letting an agent access hundreds of capabilities without overwhelming its context window.

```bash
cd pydantic-ai-skills-demo
cp .env.example .env     # Add your API key
uv sync
uv run python -m src.cli
```

**What this demonstrates:**
- **Progressive disclosure** - Skills load in 3 levels (metadata -> instructions -> resources)
- **5 working skills** - Weather, research assistant, recipe finder, world clock, code review
- **Type safety** - Full Pydantic models and typed dependencies
- **Multi-provider** - Works with OpenRouter, OpenAI, or Ollama

### `.claude/skills/pptx-generator/SKILL.md`

A real-world skill file showing how skills are structured as packaged expertise in markdown. This is the PowerPoint generator skill from the Dynamous Second Brain - a concrete example of the SKILL.md format discussed in the video.

### `diagram.excalidraw`

The Excalidraw diagram used throughout the video covering:

1. **The Old Way (2024-2025)** - Pick framework, define tools, set up RAG, wire agent loop
2. **Batteries-Included SDKs (2026)** - Claude Agent SDK, Codex, built-in tools, skills vs tools
3. **Frameworks Still Matter** - Pydantic AI, LangGraph, OpenAI Agents, CrewAI
4. **The Decision** - When to use an SDK vs a framework
5. **What Happened to RAG?** - From naive RAG to agentic RAG and hybrid approaches

## Links

- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Agent Skills Standard](https://agentskills.io)
- [Pydantic AI](https://ai.pydantic.dev/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LlamaIndex: Did Filesystem Tools Kill Vector Search?](https://www.llamaindex.ai/blog/did-filesystem-tools-kill-vector-search)
