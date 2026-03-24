// @ts-nocheck
/**
 * Claude Agent SDK - Research Agent with Custom MCP Tools
 *
 * Demonstrates:
 * - Built-in tools (Read, Write, WebSearch, Bash, Grep)
 * - Custom MCP server with your own tools
 * - Subagents for specialized tasks
 * - Hooks for monitoring tool usage
 *
 * Usage:
 *   bun run agent.ts "your research topic"
 */

import {
  query,
  createSdkMcpServer,
  tool,
  type HookCallback,
} from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import { appendFile, readFile, mkdir } from "fs/promises";
import { existsSync } from "fs";

// ============================================================================
// CUSTOM MCP TOOLS
// ============================================================================

/**
 * Save a structured research note to a file.
 * This shows WHY you'd build custom tools - the built-in Read/Write handle
 * raw files, but this adds domain logic: structured metadata, timestamps,
 * and organized storage.
 */
const saveNoteTool = tool(
  "save_note",
  "Save a research finding with structured metadata to the notes directory",
  {
    title: z.string().describe("Short title for the finding"),
    content: z.string().describe("The research finding or insight"),
    source: z.string().optional().describe("URL or source of the information"),
    tags: z.string().optional().describe("Comma-separated tags for categorization"),
  },
  async ({ title, content, source, tags }) => {
    if (!existsSync("./notes")) {
      await mkdir("./notes", { recursive: true });
    }

    const entry = {
      title,
      content,
      source: source || "unknown",
      tags: tags ? tags.split(",").map((t) => t.trim()) : [],
      timestamp: new Date().toISOString(),
    };

    await appendFile("./notes/findings.jsonl", JSON.stringify(entry) + "\n");

    return {
      content: [{ type: "text" as const, text: `Saved note: "${title}"` }],
    };
  }
);

/**
 * Search saved notes by keyword.
 * Another custom tool that adds logic beyond raw file reading -
 * it parses JSONL, searches across fields, and returns structured results.
 */
const searchNotesTool = tool(
  "search_notes",
  "Search saved research notes by keyword across titles, content, and tags",
  {
    keyword: z.string().describe("Search term to find in saved notes"),
  },
  async ({ keyword }) => {
    if (!existsSync("./notes/findings.jsonl")) {
      return {
        content: [{ type: "text" as const, text: "No notes saved yet." }],
      };
    }

    const data = await readFile("./notes/findings.jsonl", "utf-8");
    const lines = data.trim().split("\n").filter(Boolean);
    const notes = lines.map((line) => JSON.parse(line));

    const matches = notes.filter(
      (note) =>
        note.title.toLowerCase().includes(keyword.toLowerCase()) ||
        note.content.toLowerCase().includes(keyword.toLowerCase()) ||
        note.tags.some((t: string) => t.toLowerCase().includes(keyword.toLowerCase()))
    );

    if (matches.length === 0) {
      return {
        content: [{ type: "text" as const, text: `No notes found for "${keyword}".` }],
      };
    }

    const summary = matches
      .map((n) => `- **${n.title}** (${n.timestamp})\n  ${n.content}`)
      .join("\n\n");

    return {
      content: [{ type: "text" as const, text: `Found ${matches.length} notes:\n\n${summary}` }],
    };
  }
);

// Create an in-process MCP server from our custom tools
const customServer = createSdkMcpServer({
  name: "research-tools",
  version: "1.0.0",
  tools: [saveNoteTool, searchNotesTool],
});

// ============================================================================
// HOOKS
// ============================================================================

/** Log all tool usage for visibility */
const toolLogger: HookCallback = async (input) => {
  if ("tool_name" in input) {
    console.log(`  [tool] ${input.tool_name}`);
  }
  return {};
};

// ============================================================================
// SUBAGENTS
// ============================================================================

const agents = {
  researcher: {
    description: "Gathers information from the web on a given topic",
    prompt: `You are a research analyst. Search the web for information on the given topic.
Save each key finding using the save_note tool with a clear title, the finding content, and the source URL.
Focus on recent, authoritative sources. Save at least 3-5 findings.`,
    tools: ["WebSearch", "WebFetch", "save_note"],
    model: "sonnet" as const,
  },

  writer: {
    description: "Produces polished reports from research findings",
    prompt: `You are a technical writer. Use search_notes to retrieve saved findings,
then write a polished markdown report. Structure it with an executive summary,
key findings, and conclusions. Write the report to a file.`,
    tools: ["search_notes", "Read", "Write"],
    model: "sonnet" as const,
  },
};

// ============================================================================
// MAIN
// ============================================================================

async function main() {
  const topic = process.argv[2] || "How AI agent frameworks evolved in 2026";

  console.log("=".repeat(60));
  console.log("Claude Agent SDK - Research Agent");
  console.log("=".repeat(60));
  console.log(`Topic: ${topic}\n`);

  const start = Date.now();

  async function* streamPrompt() {
    yield {
      type: "user" as const,
      message: {
        role: "user" as const,
        content: [
          {
            type: "text" as const,
            text: `Research the following topic and produce a report:

**Topic:** ${topic}

**Workflow:**
1. Delegate to the "researcher" subagent to search the web and save findings
2. Delegate to the "writer" subagent to compile findings into a report
3. Output the final report path when done`,
          },
        ],
      },
    };
  }

  for await (const message of query({
    prompt: streamPrompt(),
    options: {
      // Built-in tools + custom MCP tools
      allowedTools: [
        "Task", "Read", "Write", "WebSearch", "Bash", "Grep",
        "save_note", "search_notes",
      ],

      // Specialized subagents
      agents,

      // Custom MCP server with our tools
      mcpServers: {
        custom: customServer,
      },

      // Monitor tool usage
      hooks: {
        PreToolUse: [{ hooks: [toolLogger] }],
      },

      permissionMode: "bypassPermissions",
      maxBudgetUsd: 2.0,

      systemPrompt: `You are an orchestrator agent. Today is ${new Date().toISOString().split("T")[0]}.
Coordinate between subagents to research topics and produce reports.`,
    },
  })) {
    if (message.type === "assistant" && message.message?.content) {
      for (const block of message.message.content) {
        if ("text" in block) {
          console.log(block.text);
        } else if ("name" in block) {
          if (block.name === "Task") {
            const input = block.input as { description?: string };
            console.log(`\n[Delegating: ${input.description}]\n`);
          }
        }
      }
    } else if (message.type === "result") {
      const duration = ((Date.now() - start) / 1000).toFixed(1);
      console.log(`\nDone in ${duration}s`);
      if ("total_cost_usd" in message) {
        console.log(`Cost: $${(message.total_cost_usd as number).toFixed(4)}`);
      }
    }
  }
}

main().catch(console.error);
