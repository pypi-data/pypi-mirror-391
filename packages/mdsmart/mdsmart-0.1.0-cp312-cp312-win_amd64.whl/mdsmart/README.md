# MDSmart - Multi-Database Smart Query Generator

MDSmart converts natural language questions into SQL using local LLMs via Ollama. It supports SQLite by default, with optional connectors for PostgreSQL and MySQL/MariaDB, plus a built-in FAISS vector store for training examples and a Knowledge Base for injecting business rules and documentation.

## Features

- Local LLMs with Ollama (no external keys required)
- SQLite, PostgreSQL, and MySQL/MariaDB support with automatic schema extraction (install extras for non-SQLite)
- Retrieval-augmented prompts using FAISS (examples + knowledge)
- Retry flow to fix SQL when execution fails

## Quick Start

```python
from mdsmart import MDSmart

# Initialize (ensure `ollama serve` is running)
md = MDSmart(model="llama3", embedding_model="nomic-embed-text")

# Connect to database
md.connect_database(
    db_id="sales_db",
    db_type="sqlite",
    connection_params={"path": "sales.db"},
    description="Sales and orders data",
    keywords=["sales", "orders", "revenue"]
)

# Ask a question
result = md.ask("What are the top 10 products by revenue?")
print(result)
```

## Requirements

- Python 3.8+
- Ollama installed and running
- FAISS for vector search (`pip install faiss-cpu`)

## More Documentation

- Getting Started: `docs/getting-started.md`
- API Reference: `docs/api.md`


