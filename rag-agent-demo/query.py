"""Non-interactive query interface for testing the BasicRAGAgent.

Usage:
    uv run python query.py "What is the Transformer architecture?"
    uv run python query.py "What are the BLEU scores?" --verbose
    uv run python query.py --stats
"""

import sys
import os
import asyncio
import argparse
import logging

from dotenv import load_dotenv

load_dotenv()

import asyncpg
from pydantic_ai import Agent, RunContext

from ingestion.embedder import create_embedder
from utils.providers import get_llm_model

logger = logging.getLogger(__name__)

db_pool = None


async def initialize_db():
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(
            os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
            command_timeout=60,
        )


async def search_knowledge_base(ctx: RunContext[None], query: str, limit: int = 5) -> str:
    """Search the knowledge base for relevant information."""
    global db_pool
    if not db_pool:
        await initialize_db()

    try:
        embedder = create_embedder()
        query_embedding = await embedder.embed_query(query)
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        async with db_pool.acquire() as conn:
            results = await conn.fetch(
                "SELECT * FROM match_chunks($1::vector, $2)", embedding_str, limit
            )

        if not results:
            return f"No results found for query: '{query}'"

        response_parts = []
        for i, row in enumerate(results, 1):
            similarity = row["similarity"]
            content = row["content"]
            doc_title = row["document_title"]
            response_parts.append(
                f"[Source: {doc_title} | Similarity: {similarity:.3f}]\n{content}\n"
            )

        return f"Found {len(response_parts)} relevant results:\n\n" + "\n---\n".join(
            response_parts
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search error: {e}"


agent = Agent(
    get_llm_model(),
    system_prompt="""You are an intelligent knowledge assistant with access to a document knowledge base.

IMPORTANT: Always search the knowledge base before answering questions about documents.
Use the search_knowledge_base tool to find relevant information, then synthesize a clear answer.
Always cite your sources by referencing the document titles.""",
    tools=[search_knowledge_base],
)


async def run_query(query: str, verbose: bool = False) -> str:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    await initialize_db()

    result = await agent.run(query)
    return result.output


async def show_stats():
    await initialize_db()
    async with db_pool.acquire() as conn:
        docs = await conn.fetch("SELECT count(*) as cnt FROM documents")
        chunks = await conn.fetch("SELECT count(*) as cnt FROM chunks")
        print(f"Documents: {docs[0]['cnt']}")
        print(f"Chunks: {chunks[0]['cnt']}")

        doc_list = await conn.fetch("SELECT title, source FROM documents ORDER BY created_at")
        if doc_list:
            print("\nIndexed documents:")
            for row in doc_list:
                print(f"  - {row['title']} ({row['source']})")


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Query the BasicRAGAgent")
    parser.add_argument("query", nargs="?", help="The question to ask")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--stats", action="store_true", help="Show database stats")

    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_stats())
        return

    if not args.query:
        parser.print_help()
        return

    answer = asyncio.run(run_query(args.query, verbose=args.verbose))
    print(f"\n{answer}")


if __name__ == "__main__":
    main()
