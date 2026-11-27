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

        column_details = [f"{column['name']} ({column['type']})" for column in columns]

        table_info = f"Table: {table}\nColumns: {', '.join(column_details)}"

        foreign_keys = inspector.get_foreign_keys(table)

        if foreign_keys:
            relationships = []

            for fk in foreign_keys:
                source_columns = ", ".join(fk["constrained_columns"])
                target_columns = ", ".join(fk["referred_columns"])

                relationships.append(
                    f"{source_columns} -> {fk['referred_table']}.{target_columns}"
                )

            table_info += "\nForeign Keys: " + "; ".join(relationships)

        schema.append(table_info)

    return "\n\n".join(schema)


def ask_ollama(prompt):

    result = subprocess.run(
        ["ollama", "run", "llama3.2:3b"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
        timeout=180,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def clean_sql(response):

    response = response.strip()

    response = re.sub(r"```(?:sql)?", "", response, flags=re.IGNORECASE)

    response = response.replace("```", "").strip()

    match = re.search(r"\bSELECT\b.*", response, flags=re.IGNORECASE | re.DOTALL)

    if not match:
        raise ValueError("Could not find a SELECT query in model response.")

    sql = match.group(0).strip()
    sql = sql.rstrip().rstrip(";").rstrip()

    return sql.strip()


def validate_sql(sql):

    if not sql:
        raise ValueError("SQL query cannot be empty.")

    normalized = sql.strip()

    if not re.match(r"^SELECT\b", normalized, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in normalized:
        raise ValueError("Multiple SQL statements are not allowed.")

    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "ATTACH",
        "DETACH",
        "PRAGMA",
    ]

    for word in forbidden:
        if re.search(r"\b" + word + r"\b", normalized, flags=re.IGNORECASE):
            raise ValueError(f"Unsafe SQL operation detected: {word}")

    return True


def generate_sql(question, error_message=None, schema=None):

    if schema is None:
        schema = get_database_schema()

    correction = ""

    if error_message:
        correction = f"""
PREVIOUS QUERY FAILURE:

{error_message}

CORRECTION INSTRUCTIONS:

1. Identify the exact cause of the previous failure.
2. Read the database schema again.
3. Do not repeat the previous incorrect query.
4. Verify every table and column against the schema.
5. Verify every alias is declared in FROM or JOIN.
6. Verify every JOIN uses valid columns.
7. Do not invent tables or columns.
8. Check calculations and units carefully.
9. Return one complete corrected SQLite SELECT query.
"""

    prompt = f"""
You are an expert SQLite Text-to-SQL assistant.

Convert the user's question into one correct SQLite SELECT query.

ACTUAL DATABASE SCHEMA:

{schema}

STRICT SCHEMA RULES:

1. Use only tables and columns listed in the schema.
2. Never invent tables, columns, or relationships.
3. Every alias must be declared in FROM or JOIN.
4. Verify every selected column belongs to its table.
5. Prefer simple SQL and avoid unnecessary JOINs.
6. Return one complete SELECT query.

IMPORTANT CHINOOK DATABASE FACTS:

1. Customer:
   CustomerId, FirstName, LastName, Country.

2. There is NO Country table.
   Customer.Country is a text column.

3. Invoice:
   InvoiceId, CustomerId, Total, InvoiceDate.

4. Artist:
   ArtistId, Name.

5. Album:
   AlbumId, Title, ArtistId.

6. Track:
   TrackId, Name, AlbumId, GenreId, Milliseconds, UnitPrice.

7. InvoiceLine:
   InvoiceId, TrackId, UnitPrice, Quantity.

UNIT AND CALCULATION RULES:

Track.Milliseconds stores duration in milliseconds.

IMPORTANT:
When the user asks for average track duration in MINUTES,
you MUST use:

AVG(Track.Milliseconds) / 60000.0

Do NOT divide by 1000.0 for minutes.

When the user asks for average track duration in SECONDS,
use:

AVG(Track.Milliseconds) / 1000.0

When the user asks for total or individual duration in minutes,
use:

Track.Milliseconds / 60000.0

EXAMPLE:

Question:
What is the average duration of all tracks in minutes?

Correct SQL:
SELECT AVG(Milliseconds) / 60000.0 AS AverageDurationMinutes
FROM Track;

The expected result is approximately 6.56 minutes.

Other calculation rules:

- Customer spending: SUM(Invoice.Total).
- Total revenue: SUM(Invoice.Total) from Invoice.
- Total tracks: COUNT(Track.TrackId) from Track.
- Purchased track entries: COUNT(InvoiceLine.TrackId).
- Customer counts by country: GROUP BY Customer.Country.
- Tracks by genre: JOIN Track and Genre using GenreId.
- Albums by artist: JOIN Artist and Album using ArtistId.

QUERY RULES:

1. Use COUNT, SUM, AVG, MIN and MAX appropriately.
2. Use GROUP BY for category-based aggregation.
3. Use ORDER BY for ranking.
4. Use LIMIT for top N and bottom N.
5. Use correct SQLite syntax.
6. Avoid unnecessary joins and duplicate counting.
7. Check calculation units before returning the query.

FINAL VERIFICATION:

- All tables and columns exist.
- All aliases are declared.
- JOIN conditions are valid.
- Aggregations are correct.
- Units match the user's requested units.
- The query answers the exact question.

{correction}

USER QUESTION:

{question}

Return only the SQL query.
"""

    response = ask_ollama(prompt)

    sql = clean_sql(response)

    validate_sql(sql)

    return sql
