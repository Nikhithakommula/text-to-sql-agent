# Text-to-SQL Agent

An AI-powered database assistant that converts natural-language questions into SQL queries and retrieves answers from a relational database.

## Project Overview

The Text-to-SQL Agent allows users to interact with a database using everyday language instead of writing SQL queries manually.

For example:

**User question:**
```text
How many customers are there?
```

**Generated SQL:**
```sql
SELECT COUNT(*) FROM Customer;
```

**Result:**
```text
59
```

The system uses a locally running LLM through Ollama to generate SQL queries based on the actual database schema.

## Current Features

- Natural-language question input through a command-line interface.
- Automatic database schema inspection.
- SQL query generation using Llama 3.2 (3B).
- SQL validation to restrict queries to SELECT statements.
- SQL execution using SQLAlchemy and SQLite.
- Basic result formatting.
- Retry-based SQL regeneration when a query fails.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Ollama | Running the local language model |
| Llama 3.2 (3B) | Natural-language to SQL generation |
| LangChain | LLM integration |
| SQLAlchemy | Database connection and query execution |
| SQLite | Relational database |
| LangGraph | Planned agent workflow integration |

## Project Structure

```text
text-to-sql-agent/
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
│   └── sql_executor.py
│
├── tests/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Database

This project currently uses the **Chinook SQLite sample database**.

It contains tables such as:

- Artist
- Album
- Track
- Customer
- Employee
- Invoice
- InvoiceLine
- Genre
- Playlist

The agent inspects the database schema and uses the available tables and columns when generating SQL queries.

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/text-to-sql-agent.git
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

### 4. Install and run Ollama

Install Ollama from:

https://ollama.com/

Download the model:

```bash
ollama pull llama3.2:3b
```

Make sure the Ollama service is running before starting the application.

### 5. Run the project

```bash
python main.py
```

Enter a natural-language question when prompted.

Type `exit` to close the application.

## Example Questions

```text
How many customers are there?

Show me customers from India.

Which country has the most customers?

How many albums are there?

Which customers live in London?
```

## Current Development Status

This repository contains the initial working command-line prototype.

The current implementation supports basic natural-language SQL generation and database querying. Complex JOIN queries may still require improvements to SQL generation and error correction.

## Planned Improvements

- Improve SQL generation and error handling.
- Implement a structured agent workflow using LangGraph.
- Improve automatic SQL correction and validation.
- Develop an interactive Streamlit dashboard.
- Build a REST API.
- Add comprehensive testing and documentation.

## Project Goal

To build an agentic AI database assistant that makes relational databases easier to access through natural-language conversations, without requiring users to write SQL manually.

---

**Project Status:** In Development