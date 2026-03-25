# Docling RAG CLI Agent

An intelligent text-based CLI agent that provides conversational access to a knowledge base stored in PostgreSQL with PGVector. Uses RAG (Retrieval Augmented Generation) to search through embedded documents and provide contextual, accurate responses with source citations.

## Features

- 💬 Interactive text-based CLI with streaming responses
- 🔍 Semantic search through vector-embedded documents
- 📚 Context-aware responses using RAG pipeline
- 🎯 Source citation for all information provided
- 🔄 Real-time streaming text output as tokens arrive
- 💾 PostgreSQL/PGVector for scalable knowledge storage
- 🧠 Conversation history maintained across turns

## Prerequisites

- Python 3.9 or later
- PostgreSQL with PGVector extension (Supabase, Neon, self-hosted Postgres, etc.)
- API Keys:
  - OpenAI API key (for embeddings and LLM)

## Quick Start

### 1. Install Dependencies

```bash
# Install dependencies using UV
uv sync
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - Neon serverless Postgres connection string with PGVector extension
  - Get yours at https://console.neon.tech → Connection Details → Connection string
  - Example: `postgresql://[user]:[password]@[endpoint].neon.tech/[dbname]?sslmode=require`

- `OPENAI_API_KEY` - OpenAI API key for embeddings and LLM
  - Get from: https://platform.openai.com/api-keys

Optional variables:
- `LLM_CHOICE` - OpenAI model to use (default: `gpt-4o-mini`)
- `EMBEDDING_MODEL` - Embedding model (default: `text-embedding-3-small`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### 3. Configure Database

You must set up your PostgreSQL database with the PGVector extension and create the required schema:

1. **Enable PGVector extension** in your database (most cloud providers have this pre-installed)
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Run the schema file** to create tables and functions:
   ```bash
   # Using psql
   psql $DATABASE_URL < sql/schema.sql

   # Or connect to your database and run the SQL directly
   ```

The schema file (`sql/schema.sql`) creates:
- `documents` table for storing original documents with metadata
- `chunks` table for text chunks with 1536-dimensional embeddings
- `match_chunks()` function for vector similarity search

### 4. Ingest Documents

Add your documents to the `documents/` folder (supports markdown, text files), then run:

```bash
# Ingest all documents in the documents/ folder
uv run python -m ingestion.ingest --documents documents/

# Clean existing data before ingestion
uv run python -m ingestion.ingest --documents documents/ --clean

# Adjust chunk size (default: 1000)
uv run python -m ingestion.ingest --documents documents/ --chunk-size 800

# Verbose output
uv run python -m ingestion.ingest --documents documents/ -v
```

The ingestion pipeline will:
1. Read markdown/text documents from the folder
2. Split them into semantic chunks
3. Generate embeddings using OpenAI
4. Store chunks and embeddings in PostgreSQL

### 5. Run the Agent

You have two options for running the agent:

#### Option 1: Enhanced CLI (Recommended)

The enhanced CLI provides a better user experience with colors, formatting, and additional commands:

```bash
# Run the enhanced CLI
uv run python cli.py

# With verbose logging
uv run python cli.py --verbose

# Use a different model
uv run python cli.py --model gpt-4o
```

**Features:**
- 🎨 **Colored output** for better readability
- 📊 **Session statistics** (`stats` command)
- 🔄 **Clear history** (`clear` command)
- 💡 **Built-in help** (`help` command)
- ✅ **Database health check** on startup
- 🔍 **Real-time streaming** responses

**Available commands:**
- `help` - Show help information
- `clear` - Clear conversation history
- `stats` - Show session statistics
- `exit` or `quit` - Exit the CLI

**Example interaction:**
```
============================================================
🤖 Docling RAG Knowledge Assistant
============================================================
AI-powered document search with streaming responses
Type 'exit', 'quit', or Ctrl+C to exit
Type 'help' for commands
============================================================

✓ Database connection successful
✓ Knowledge base ready: 20 documents, 156 chunks
Ready to chat! Ask me anything about the knowledge base.

You: What topics are covered in the knowledge base?
🤖 Assistant: Based on the knowledge base, the main topics include...

────────────────────────────────────────────────────────────
You: quit
👋 Thank you for using the knowledge assistant. Goodbye!
```

#### Option 2: Basic CLI

A simpler, minimal CLI without colors or extra features:

```bash
# Run the basic CLI
uv run python rag_agent.py
```

**Features:**
- Simple text-based interface
- Streaming responses
- Conversation history
- Basic exit commands

**Example interaction:**
```
============================================================
RAG Knowledge Assistant
============================================================
Ask me anything about the knowledge base!
Type 'quit', 'exit', or press Ctrl+C to exit.
============================================================

You: What is the capital of France?
Assistant: Based on the knowledge base, the capital of France is Paris...

You: Tell me more about it
Assistant: Paris is located...

You: quit
Assistant: Thank you for using the knowledge assistant. Goodbye!
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CLI User  │────▶│  RAG Agent   │────▶│ PostgreSQL  │
│   (Input)   │     │ (PydanticAI) │     │  PGVector   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼────┐  ┌────▼─────┐
              │  OpenAI  │  │  OpenAI  │
              │   LLM    │  │Embeddings│
              └──────────┘  └──────────┘
```

## Model Configuration

- **LLM**: OpenAI GPT-4o-mini (fast, cost-effective)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Framework**: PydanticAI for agent orchestration
- **Streaming**: Real-time token streaming via `run_stream()`

## Key Components

### RAG Agent

The main agent (`rag_agent.py`) that:
- Manages database connections with connection pooling
- Handles interactive CLI with streaming responses
- Performs knowledge base searches via RAG
- Tracks conversation history for context

### search_knowledge_base Tool

Function tool registered with the agent that:
- Generates query embeddings using OpenAI
- Searches using PGVector cosine similarity
- Returns top-k most relevant chunks
- Formats results with source citations

Example tool definition:
```python
async def search_knowledge_base(
    ctx: RunContext[None],
    query: str,
    limit: int = 5
) -> str:
    """Search the knowledge base using semantic similarity."""
    # Generate embedding for query
    # Search PostgreSQL with PGVector
    # Format and return results
```

### Database Schema

- `documents`: Stores original documents with metadata
  - `id`, `title`, `source`, `content`, `metadata`, `created_at`, `updated_at`

- `chunks`: Stores text chunks with vector embeddings
  - `id`, `document_id`, `content`, `embedding` (vector(1536)), `chunk_index`, `metadata`, `token_count`

- `match_chunks()`: PostgreSQL function for vector similarity search
  - Uses cosine similarity (`1 - (embedding <=> query_embedding)`)
  - Returns chunks with similarity scores above threshold

## Performance Optimization

### Database Connection Pooling
```python
db_pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=2,
    max_size=10,
    command_timeout=60
)
```

### Embedding Cache
The embedder includes built-in caching for frequently searched queries, reducing API calls and latency.

### Streaming Responses
Token-by-token streaming provides immediate feedback to users while the LLM generates responses:
```python
async with agent.run_stream(user_input, message_history=history) as result:
    async for text in result.stream_text(delta=False):
        print(f"\rAssistant: {text}", end="", flush=True)
```

## Testing

### Run Unit Tests

```bash
uv run pytest tests/test_rag_agent.py -v
```

### Run Behavioral Tests

```bash
uv run pytest tests/test_behaviors.py -v
```

### Run All Tests

```bash
uv run pytest tests/ -v
```

## Monitoring

### Logging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uv run python rag_agent.py
```

Logs include:
- Database connection status
- RAG search queries and results
- LLM interactions
- Error traces

### Metrics to Track

- RAG search latency (embedding + vector search)
- Embedding generation time
- Database query performance
- Token usage per query (input + output)
- Conversation turn count
- Knowledge base hit rate

## CLI Usage

### Enhanced CLI (cli.py)

The recommended way to interact with the agent:

```bash
# Standard usage
uv run python cli.py

# Verbose logging
uv run python cli.py --verbose

# Use different model
uv run python cli.py --model gpt-4o
```

**Features:**
- 🎨 Colored, formatted output
- 📊 Session statistics
- 🔄 Clear conversation history
- 💡 Built-in help system
- ✅ Database health checks

**Commands:**
- `help` - Show available commands
- `clear` - Clear conversation history
- `stats` - Show session statistics
- `exit`/`quit` - Exit the CLI

### Basic CLI (rag_agent.py)

Simple CLI without colors or extra features:

```bash
# Standard usage
uv run python rag_agent.py
```

**Features:**
- Simple text interface
- Streaming responses
- Conversation history
- Basic commands: `quit`, `exit`, `bye`

### Environment Variables at Runtime

Both CLIs support runtime environment variable overrides:

```bash
# Use different model
LLM_CHOICE=gpt-4o uv run python cli.py

# Enable debug logging
LOG_LEVEL=DEBUG uv run python cli.py

# Use different database
DATABASE_URL=postgresql://... uv run python cli.py
```

## API Reference

### search_knowledge_base Tool

```python
async def search_knowledge_base(
    ctx: RunContext[None],
    query: str,
    limit: int = 5
) -> str:
    """
    Search the knowledge base using semantic similarity.

    Args:
        query: The search query to find relevant information
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted search results with source citations
    """
```

### Database Functions

```sql
-- Vector similarity search
SELECT * FROM match_chunks(
    query_embedding::vector(1536),
    match_count INT,
    similarity_threshold FLOAT DEFAULT 0.7
)
```

Returns chunks with:
- `id`: Chunk UUID
- `content`: Text content
- `embedding`: Vector embedding
- `similarity`: Cosine similarity score (0-1)
- `document_title`: Source document title
- `document_source`: Source document path

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Verify PGVector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'vector'"
```

### Missing Embeddings

If search returns no results, ensure documents are ingested:
```bash
# Check documents table
psql $DATABASE_URL -c "SELECT COUNT(*) FROM documents"

# Check chunks table
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks"
```

### OpenAI API Errors

- Verify API key is valid: https://platform.openai.com/api-keys
- Check rate limits and quotas
- Ensure billing is set up

## Project Structure

```
docling-rag-agent/
├── cli.py                   # Enhanced CLI with colors and features (recommended)
├── rag_agent.py             # Basic CLI agent with PydanticAI
├── ingestion/
│   ├── ingest.py            # Document ingestion pipeline
│   ├── embedder.py          # Embedding generation with caching
│   └── chunker.py           # Document chunking logic
├── utils/
│   ├── providers.py         # OpenAI model/client configuration
│   ├── db_utils.py          # Database connection pooling
│   └── models.py            # Pydantic models for config
├── sql/
│   └── schema.sql           # PostgreSQL schema with PGVector
├── documents/               # Sample documents for ingestion
├── pyproject.toml           # Project dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review the code examples in `rag_agent.py` and `ingestion/`