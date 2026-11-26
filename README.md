# Text-to-SQL Agent

An AI-powered database assistant that converts natural-language questions into SQL queries and retrieves answers from a relational database.

The project uses a locally running LLM through Ollama to understand user questions, generate SQL queries based on the database schema, execute them, and present the results in a readable format.

## Project Overview

The Text-to-SQL Agent allows users to interact with a relational database using everyday language instead of writing SQL manually.

**Example**

User question:

```text
How many customers are there?
```

Generated SQL:

```sql
SELECT COUNT(*) FROM Customer;
```

Result:

```text
Customer count: 59
```

The system inspects the actual database schema before generating queries, helping the LLM use available tables and columns.

## Current Features

- Natural-language question input through a command-line interface.
- Automatic database schema inspection.
- SQL generation using the local Llama 3.2 (3B) model.
- Schema-aware prompts to reduce invalid table and column references.
- SQL parsing and validation using SQLGlot.
- SELECT-only query restrictions and protection against multiple SQL statements.
- SQL execution using SQLAlchemy and SQLite.
- Automatic SQL regeneration when validation or execution fails.
- Up to three attempts for query generation and correction.
- Readable result formatting with column names and limited row previews.
- Automated tests for database connectivity, SQL validation, execution, and agent workflows.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Ollama | Local LLM execution |
| Llama 3.2 (3B) | Natural-language to SQL generation |
| SQLAlchemy | Database connection and query execution |
| SQLite | Relational database |
| SQLGlot | SQL parsing and validation |
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
│   ├── test_database.py
│   ├── test_sql_executor.py
│   └── test_sql_validator.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Database

The project currently uses the **Chinook SQLite sample database**.

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

The agent inspects the database schema and uses the available tables and columns when generating SQL queries.

## How It Works

1. **User Input:** The user enters a question in natural language.
2. **Schema Inspection:** The system retrieves database schema information.
3. **SQL Generation:** The local LLM generates a SQL query based on the question and schema.
4. **SQL Validation:** SQLGlot checks the query, while additional checks restrict unsafe operations.
5. **Query Execution:** Valid queries are executed against the SQLite database.
6. **Error Handling:** If validation or execution fails, the error is passed back for another SQL generation attempt.
7. **Result Formatting:** The retrieved records are formatted into a readable answer.

The agent allows up to three attempts to generate and execute a valid query.

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

```bash
python main.py
```

Enter a natural-language question when prompted.

Type `exit`, `quit`, or `q` to close the application.

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

The project currently includes **42 automated tests** covering:

- Database connectivity and schema inspection.
- SQL query validation and safety checks.
- SQL execution and error handling.
- Agent execution and retry workflows.
- Result formatting.

## Current Development Status

The project currently has a working command-line implementation with local LLM-based SQL generation, database querying, validation, retry handling, and automated testing.

SQL execution and validation do not guarantee that every generated query is semantically correct. Improving query accuracy and handling more complex questions remain ongoing goals.

## Planned Improvements

- Implement a structured agent workflow using LangGraph.
- Improve SQL generation and semantic accuracy.
- Strengthen automatic SQL correction and error handling.
- Develop an interactive Streamlit interface.
- Build a REST API using FastAPI.
- Expand testing with more complex natural-language queries.

## Project Goal

To build an agentic AI database assistant that makes relational databases easier to access through natural-language conversations, without requiring users to write SQL manually.

---

**Project Status:** In Development