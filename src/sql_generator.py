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

        column_details = []

        for column in columns:
            column_details.append(f"{column['name']} ({column['type']})")

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


def generate_sql(question, error_message=None):

    schema = get_database_schema()

    correction = ""

    if error_message:
        correction = f"""
IMPORTANT: YOUR PREVIOUS SQL QUERY FAILED.

PREVIOUS QUERY AND ERROR:

{error_message}

YOU MUST FIX THE ACTUAL ERROR.

Before generating the new SQL:

1. Read the complete database schema again.
2. Check every table alias used in SELECT, WHERE,
   GROUP BY, ORDER BY and JOIN conditions.
3. Every alias must be declared in FROM or JOIN.
4. Never use an undeclared table alias.
5. Do not repeat the previous incorrect SQL.
6. Use the correct table for the requested entity
   and its attributes.
7. Check all JOIN conditions against foreign keys.
8. Check that the selected columns belong to the
   intended tables.
9. Return one corrected SQLite SELECT query only.
"""

    prompt = f"""
You are an expert SQLite Text-to-SQL assistant.

Convert the user's natural-language question into
exactly one valid SQLite SELECT query.

DATABASE SCHEMA:

{schema}

IMPORTANT SQL GENERATION RULES:

1. Use only tables and columns present in the schema.
2. Never invent table names or column names.
3. Follow actual foreign-key relationships for JOINs.
4. Use COUNT, SUM, AVG, MIN and MAX when appropriate.
5. Use GROUP BY for category-based results.
6. Use ORDER BY when ranking or sorting is requested.
7. Use LIMIT only when the user requests top N,
   bottom N, highest or lowest records.
8. Use valid SQLite date functions.
9. Generate only one SELECT query.
10. Never generate data modification statements.
11. Do not include explanations or Markdown code fences.
12. Every table alias must be declared in FROM or JOIN.
13. Verify that every selected column belongs to
    the correct table.

UNIT AND CALCULATION RULES:

1. Track.Milliseconds stores duration in milliseconds.
2. Convert milliseconds to seconds using / 1000.0.
3. Convert milliseconds to minutes using / 60000.0.
4. For average track duration in minutes,
   use AVG(Track.Milliseconds) / 60000.0.
5. For customer spending, use Invoice.Total.
6. For total revenue, use SUM(Invoice.Total).

IMPORTANT CHINOOK DATABASE RULES:

1. To count all tracks:
   Count Track.TrackId directly from Track.
   Do not join InvoiceLine or PlaylistTrack.

2. To count purchased track entries:
   Use InvoiceLine.TrackId.

3. To count albums by artist:
   Join Artist and Album using ArtistId.

4. To find the artist with the most albums:
   Count Album.AlbumId and select Artist.Name.

5. To count customers:
   Count Customer.CustomerId.

6. To calculate customer spending:
   Join Customer and Invoice using CustomerId.
   Calculate SUM(Invoice.Total).

7. To calculate total revenue:
   Use SUM(Invoice.Total) from Invoice.

8. To count tracks by genre:
   Join Track and Genre using GenreId.
   Count Track.TrackId.

9. CUSTOMER COUNTRY ANALYSIS:
   When asked for customer counts by country:
   - Use Customer.Country.
   - Group by Customer.Country.
   - Count Customer.CustomerId.
   - Do not use Employee.Country.
   - Do not join Employee unless explicitly required.

10. GENERAL ENTITY ATTRIBUTE RULE:
    Identify the main entity in the user's question.
    Use attributes belonging to that entity.
    Do not use a similarly named column from a
    related table unless explicitly requested.

11. ENTITY COUNTING RULE:
    When asked for the total number of records
    belonging to an entity, count its primary key
    directly from that entity's table.
    Avoid unnecessary JOINs.

QUERY REQUIREMENTS:

- Select only columns needed to answer the question.
- Use meaningful aliases for calculated columns.
- Avoid unnecessary JOINs.
- Ensure aggregation matches the requested entity.
- Verify JOIN conditions and aliases.
- Ensure the SQL answers the exact user question.

{correction}

USER QUESTION:

{question}

Return only the SQL query.
"""

    response = ask_ollama(prompt)

    sql = clean_sql(response)

    validate_sql(sql)

    return sql
