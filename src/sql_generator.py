import os
import re
import subprocess
from sqlalchemy import create_engine, inspect


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "Chinook.sqlite")

engine = create_engine(f"sqlite:///{DATABASE_PATH}")


def get_database_schema():
    inspector = inspect(engine)

    schema = []

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)

        column_names = [column["name"] for column in columns]

        schema.append(f"Table: {table}\nColumns: {', '.join(column_names)}")

    return "\n\n".join(schema)


def ask_ollama(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3.2:3b"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


def clean_sql(response):
    response = response.strip()

    response = re.sub(r"```sql", "", response, flags=re.IGNORECASE)

    response = response.replace("```", "").strip()

    match = re.search(r"(SELECT\b.*)", response, flags=re.IGNORECASE | re.DOTALL)

    if not match:
        raise ValueError("Could not find a SELECT query.")

    sql = match.group(1).strip()

    if sql.endswith(";"):
        sql = sql[:-1]

    return sql


def validate_sql(sql):
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE"]

    upper_sql = sql.upper()

    if not upper_sql.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    for word in forbidden:
        if re.search(r"\b" + word + r"\b", upper_sql):
            raise ValueError(f"Unsafe SQL operation detected: {word}")

    return True


def generate_sql(question, error_message=None):
    schema = get_database_schema()

    correction = ""

    if error_message:
        correction = f"""
The previous SQL failed with this database error:

{error_message}

Generate a corrected SQL query.
Do not repeat the same mistake.
"""

    prompt = f"""
You are a Text-to-SQL system for a SQLite database.

Convert the user's natural-language question into ONE valid SQLite SELECT query.

DATABASE SCHEMA:

{schema}

IMPORTANT RULES:

1. Use ONLY tables that exist in the schema.
2. Use ONLY columns that exist in the schema.
3. NEVER invent tables.
4. NEVER invent columns.
5. Customer country is Customer.Country.
6. Customer city is Customer.City.
7. Customer name is Customer.FirstName and Customer.LastName.
8. Use JOIN only when necessary.
9. Do not create fake Country or Address tables.
10. For "most", use GROUP BY, ORDER BY COUNT(*) DESC and LIMIT 1 when appropriate.
11. Use SQLite syntax.
12. Only generate SELECT queries.
13. Return ONLY SQL.
14. Do not explain anything.

Example:

Question:
How many customers are from Brazil?

SQL:
SELECT COUNT(*) FROM Customer WHERE Country = 'Brazil'

Example:

Question:
Which country has the most customers?

SQL:
SELECT Country, COUNT(*) AS customer_count
FROM Customer
GROUP BY Country
ORDER BY customer_count DESC
LIMIT 1

Example:

Question:
Show me the names of customers from Canada.

SQL:
SELECT FirstName, LastName
FROM Customer
WHERE Country = 'Canada'

Example:

Question:
Which customers live in London?

SQL:
SELECT FirstName, LastName
FROM Customer
WHERE City = 'London'

{correction}

USER QUESTION:

{question}

Return ONLY the SQL query.
"""

    response = ask_ollama(prompt)

    sql = clean_sql(response)

    validate_sql(sql)

    return sql
