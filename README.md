# Text-to-SQL Agent

An agentic AI-powered database assistant that converts natural-language questions into SQL queries and retrieves answers from a relational database.

The project uses a locally running LLM through Ollama, LangGraph for workflow orchestration, SQLGlot for SQL validation, and SQLAlchemy for database execution. Users can interact with the system through a command-line interface, Streamlit web application, or FastAPI REST API.

## Project Overview

The Text-to-SQL Agent allows users to interact with a relational database using everyday language instead of writing SQL manually.

**Example**

User question:

```text
How many customers are there?
```

Generated SQL:

```sql
SELECT COUNT(CustomerId) FROM Customer
```

Result:

```text
COUNT(CustomerId): 59
```

The system inspects the actual database schema before generating queries, helping the LLM use available tables and columns.

## Features

- Natural-language question processing.
- Automatic database schema inspection.
- Local LLM integration using Ollama and Llama 3.2 (3B).
- Schema-aware SQL generation.
- SQL parsing and validation using SQLGlot.
- SELECT-only query restrictions and protection against multiple SQL statements.
- SQL execution using SQLAlchemy and SQLite.
- Automatic error detection and SQL regeneration.
- Up to three attempts for query generation and correction.
- Agent workflow orchestration using LangGraph.
- Interactive web interface using Streamlit.
- REST API endpoints using FastAPI.
- Automatic result formatting.
- Automated testing using Pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Ollama | Local LLM execution |
| Llama 3.2 (3B) | Natural-language to SQL generation |
| LangGraph | Agent workflow orchestration |
| LangChain | LLM integration |
| SQLAlchemy | Database connection and execution |
| SQLite | Relational database |
| SQLGlot | SQL parsing and validation |
| Streamlit | Interactive web interface |
| FastAPI | REST API development |
| Uvicorn | API server |
| Pytest | Automated testing |

## Project Structure

```text
text-sql-agent/
│
├── data/
│   └── Chinook.sqlite
│
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── inspect.py
│   │   └── __init__.py
│   │
│   ├── tools/
│   │   └── __init__.py
│   │
│   ├── llm.py
│   ├── sql_generator.py
│   ├── sql_executor.py
│   └── sql_validator.py
│
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_sql_executor.py
│   └── test_sql_validator.py
│
├── app.py
├── api.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Database

The project uses the **Chinook SQLite sample database**.

It contains 11 tables:

- Artist
- Album
- Track
- Customer
- Employee
- Invoice
- InvoiceLine
- Genre
- MediaType
- Playlist
- PlaylistTrack

The agent dynamically inspects the database schema and uses the available tables, columns, and relationships when generating SQL queries.

## Agent Workflow

The agent uses LangGraph to coordinate the following steps:

1. **Schema Retrieval:** Retrieves the database schema.
2. **SQL Generation:** Uses the local LLM to generate SQL based on the user's question and database schema.
3. **SQL Validation:** Validates SQL syntax and checks database compatibility and safety.
4. **Query Execution:** Executes valid SQL queries against SQLite.
5. **Error Handling:** Sends validation or execution errors back for SQL correction.
6. **Answer Formatting:** Converts database results into readable answers.

The workflow supports up to three attempts to generate and execute a valid query.

## Application Interfaces

### 1. Command-Line Interface

Run the application:

```bash
python main.py
```

Enter natural-language questions in the terminal.

### 2. Streamlit Web Application

Start the Streamlit interface:

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Users can enter questions, view generated SQL, check execution status, and inspect database results.

### 3. FastAPI REST API

Start the API server:

```bash
python -m uvicorn api:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

**Available Endpoints**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API home |
| GET | `/health` | Health check |
| POST | `/ask` | Submit a natural-language database question |

**Example API Request**

```json
{
  "question": "How many customers are there?"
}
```

**Example API Response**

```json
{
  "success": true,
  "sql": "SELECT COUNT(CustomerId) FROM Customer",
  "columns": ["COUNT(CustomerId)"],
  "rows": [[59]],
  "answer": "COUNT(CustomerId): 59",
  "attempts": 1,
  "error": null
}
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nikhithakommula/text-to-sql-agent.git
cd text-to-sql-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama:

https://ollama.com/

Pull the required model:

```bash
ollama pull llama3.2:3b
```

Make sure the Ollama service is running before starting the application.

### 5. Run the application

Choose one of the available interfaces:

**CLI**

```bash
python main.py
```

**Streamlit**

```bash
python -m streamlit run app.py
```

**FastAPI**

```bash
python -m uvicorn api:app --reload
```

## Example Questions

```text
How many customers are there?

Show me the names of customers from India.

Which artist has the most albums?

What is the total revenue generated from all invoices?

Find the top 3 countries based on the number of customers.

What is the average duration of all tracks in minutes?
```

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

**Current Test Results: 47 Passed**

The automated tests cover:

- Database connectivity and schema inspection.
- SQL query validation and safety checks.
- SQL execution and error handling.
- Agent execution and retry workflows.
- Result formatting.
- API endpoints and request validation.

## Current Development Status

The project currently includes:

- Working command-line interface.
- Local LLM-based SQL generation.
- LangGraph-based agent workflow.
- SQL validation and automatic correction.
- SQLite database integration.
- Interactive Streamlit web interface.
- FastAPI REST API.
- 47 passing automated tests.

SQL validation and successful execution do not guarantee that every generated query is semantically correct. Improving query accuracy and handling more complex questions remain ongoing goals.

## Future Improvements

- Improve SQL generation and semantic accuracy.
- Support more complex database queries.
- Expand testing with additional databases and questions.
- Improve the user interface and query history.
- Add result export capabilities.

## Project Goal

To build an agentic AI database assistant that makes relational databases easier to access through natural-language conversations, without requiring users to write SQL manually.

---

**Project Status:** In Development
