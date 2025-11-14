# MDSmart – Multi‑Database Smart Query Generator

MDSmart converts natural language questions into SQL using a local LLM (via Ollama), with optional retrieval of relevant examples and knowledge to improve accuracy. It includes a lightweight retry flow that corrects SQL when execution fails.

Key traits:
- Local-first: uses Ollama’s HTTP API; no external API keys required
- Works with SQLite out of the box; PostgreSQL and MySQL/MariaDB supported via optional connectors
- Retrieval-augmented: searches your training examples and knowledge documents
- Error-aware: retries with context from prior errors to fix SQL
- Persistent stores: FAISS-based vector indexes saved to `./mdsmart_data`


## Installation

Prerequisites:
- Python 3.8+
- Ollama installed and running (`ollama serve`) and models pulled (e.g., `ollama pull llama3` and `ollama pull nomic-embed-text`)

Install Python dependencies:
- From source: `pip install -r requirements.txt`

Note on embeddings: This project uses Ollama’s embeddings endpoint. For best results, use an embedding model such as `nomic-embed-text`. FAISS is used for vector search; install `faiss-cpu` if it’s not already present in your environment:
- `pip install faiss-cpu`


## Quick Start

Example with a local SQLite database and a few training examples:

```python
import sqlite3
from mdsmart import MDSmart

# 1) Create a small demo database
conn = sqlite3.connect("demo.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
  customer_id INTEGER PRIMARY KEY,
  name TEXT,
  country TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  amount REAL,
  status TEXT
)
""")
conn.commit(); conn.close()

# 2) Initialize MDSmart (Ollama must be running)
md = MDSmart(model="llama3", embedding_model="nomic-embed-text")

# 3) Connect to the database
md.connect_database(
    db_id="demo_db",
    db_type="sqlite",
    connection_params={"path": "demo.db"},
    description="Demo DB with customers and orders",
    keywords=["customers", "orders", "sales"]
)

# 4) Add a few NL↔SQL training examples
md.train_bulk([
    {"question": "How many customers?", "sql": "SELECT COUNT(*) AS customer_count FROM customers;"},
    {"question": "Show all orders", "sql": "SELECT * FROM orders;"}
])

# 5) Ask in natural language
df = md.ask("How many customers do we have?")
print(df)
```


## How It Works

- Database schema: The library extracts schema details (SQLite, PostgreSQL, MySQL/MariaDB) and includes them in the LLM prompt.
- Retrieval: Relevant examples (from the training vector store) and documents (from the knowledge base) are fetched via FAISS similarity search and injected into the prompt.
- SQL generation: A prompt is sent to Ollama’s `/api/generate` using the configured model (e.g., `llama3`).
- Retry on error: If execution fails, MDSmart can regenerate SQL with the previous error message and schema context to correct the query.


## Core Concepts

- Training examples (VectorStore): pairs of “question” and “sql” used as few-shot hints. Stored in FAISS and persisted to `./mdsmart_data/mdsmart_training.*`.
- Knowledge base (KnowledgeBase): longer-form business rules and documentation to guide the model. Stored in FAISS and persisted to `./mdsmart_data/mdsmart_knowledge.*`.
- Databases (DatabaseManager): registry of connections. SQLite ships by default; PostgreSQL and MySQL/MariaDB connectors are available.
- Configuration (MDSmartConfig): default model names, retrieval limits, and persistence paths.


## Usage Guide

Connecting a database:

```python
md.connect_database(
  db_id="sales_db",
  db_type="sqlite",
  connection_params={"path": "sales.db"},
  description="Sales and orders data",
  keywords=["sales", "orders", "revenue"]
)
print(md.list_databases())
```

Adding training examples:

```python
md.train(question="How many orders?", sql="SELECT COUNT(*) AS c FROM orders;")
md.train_bulk([
  {"question": "Total completed revenue",
   "sql": "SELECT SUM(amount) AS total FROM orders WHERE status='completed';"}
])
```

Working with the knowledge base:

```python
md.add_knowledge(
  content="Revenue must exclude cancelled orders.",
  doc_type="business_logic",
  title="Revenue rule"
)

# Or load from files / directories
md.load_knowledge("docs/business_rules.md", doc_type="business_logic")
md.load_knowledge_directory("docs", pattern="*.md")
```

Asking questions with retries:

```python
df = md.ask("Revenue by status last month", verbose=True, max_retries=3)
```

Export/import training examples:

```python
md.export_training("training.json")
md.import_training("training.json")
```


## API Reference (Overview)

MDSmart
- `connect_database(db_id, db_type, connection_params, description="", keywords=None)`
- `list_databases() -> pandas.DataFrame`
- `train(question, sql, db_id=None, metadata=None) -> str`
- `train_bulk(examples: List[Dict]) -> List[str]`
- `add_knowledge(content, doc_type="documentation", title=None, metadata=None) -> List[str]`
- `load_knowledge(filepath, doc_type=None) -> List[str]`
- `load_knowledge_directory(directory, pattern="*.txt", doc_type=None) -> Dict[str, List[str]]`
- `ask(question, db_id=None, verbose=False, max_retries=3) -> pandas.DataFrame`
- `get_stats() -> Dict`
- `export_training(filepath)` / `import_training(filepath)`

VectorStore (training examples)
- `add_example(question, sql, metadata=None, doc_id=None) -> str`
- `add_examples_batch(examples: List[Dict]) -> List[str]`
- `retrieve_relevant(query, top_k=3, where=None, min_similarity=0.0) -> List[Dict]`
- `get_all_examples() -> pandas.DataFrame`
- `delete_example(doc_id) -> bool`, `update_example(doc_id, ...) -> bool`, `clear()`
- `count() -> int`, `get_stats() -> Dict`, `export_to_json(path)`, `import_from_json(path)`

KnowledgeBase (documents)
- `add_document(content, doc_type, title=None, metadata=None, chunk=True) -> List[str]`
- `add_from_file(path, doc_type=None) -> List[str]`, `add_from_directory(dir, pattern="*.txt", doc_type=None) -> Dict`
- `search(query, doc_type=None, top_k=3) -> List[Dict]`, `count() -> int`, `get_stats() -> Dict`

DatabaseManager (internal; surfaced via `MDSmart.db_manager`)
- `add_database(...) -> DatabaseConnection`
- `list_databases() -> pandas.DataFrame`
- `get_combined_schema(db_ids: List[str]) -> str`

Exceptions
- `MDSmartError`, `DatabaseConnectionError`, `SQLGenerationError`, `SQLExecutionError`, `KnowledgeBaseError`


## Configuration

`MDSmartConfig` fields (defaults shown):
- `model_name="llama3"`, `ollama_url="http://localhost:11434"`, `embedding_model="nomic-embed-text"`
- Retrieval: `max_training_examples=3`, `max_knowledge_docs=2`
- Features: `auto_fix_sql=True`, `use_knowledge_base=True`
- Persistence: `persist_directory="./mdsmart_data"`, `training_collection="mdsmart_training"`, `knowledge_collection="mdsmart_knowledge"`

You can create a config and pass it to `MDSmart(config=...)`.


## Examples

See runnable examples in:
- `mdsmart/examples/basic_usage.py`
- `mdsmart/examples/knowledge_base.py`
- `basic_usage.py` (root)


## Limitations

- Database support: SQLite is first-class. PostgreSQL and MySQL/MariaDB require installing optional extras (see requirements) but are fully supported.
- Embedding model: ensure you pull and use an embeddings-capable model (e.g., `nomic-embed-text`) in Ollama. The generation model (e.g., `llama3`) can be different from the embedding model.
- Ollama availability: the library checks Ollama at init; make sure it is running and accessible at `ollama_url`.


## License

MIT License. See `LICENSE`.

cd "F:\Future Links\projects\MDsmart"; .\.venv\Scripts\Activate.ps1; python -c "import sys, pathlib; sys.path.insert(0, str(pathlib.Path.cwd())); exec(open('test_scripts\\mysql_connect.py.py','r',encoding='utf-8').read()) PY
