
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

        column_details = [
            f"{column['name']} ({column['type']})"
            for column in columns
        ]

        table_info = f"Table: {table}\nColumns: {', '.join(column_details)}"

        foreign_keys = inspector.get_foreign_keys(table)

        if foreign_keys:
            relationships = []

            for fk in foreign_keys:
                source_columns = ", ".join(fk["constrained_columns"])
                target_columns = ", ".join(fk["referred_columns"])

                relationships.append(
                    f"{source_columns} -> "
                    f"{fk['referred_table']}.{target_columns}"
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

    response = re.sub(
        r"```(?:sql)?",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = response.replace("```", "").strip()

    match = re.search(
        r"\bSELECT\b.*",
        response,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:
        raise ValueError(
            "Could not find a SELECT query in model response."
        )

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
        if re.search(
            r"\b" + word + r"\b",
            normalized,
            flags=re.IGNORECASE
        ):
            raise ValueError(f"Unsafe SQL operation detected: {word}")

    return True


def generate_sql(
    question,
    error_message=None,
    schema=None,
    previous_sql=None
):

    if schema is None:
        schema = get_database_schema()

    correction = ""

    if error_message:
        correction = f"""
PREVIOUS QUERY FAILURE:

{error_message}

PREVIOUS SQL QUERY:

{previous_sql if previous_sql else "Not available"}

CORRECTION INSTRUCTIONS:

1. Identify what was wrong with the previous SQL query.
2. Use the actual database schema to correct it.
3. Do not repeat the same incorrect query.
4. Verify every table and column against the schema.
5. Verify every alias is declared in FROM or JOIN.
6. Verify every JOIN uses valid columns.
7. Do not invent tables or columns.
8. Check aggregation functions and calculation units.
9. Return one complete corrected SQLite SELECT query.
"""

    prompt = f"""
You are an expert SQLite Text-to-SQL assistant.

Convert the user's question into one accurate SQLite SELECT query.

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

3. There is NO CustomerName column.
   To display a customer's name, use FirstName and LastName.

4. Invoice:
   InvoiceId, CustomerId, Total, InvoiceDate.

5. Artist:
   ArtistId, Name.

6. Album:
   AlbumId, Title, ArtistId.

7. Track:
   TrackId, Name, AlbumId, GenreId, Milliseconds, UnitPrice.

8. Genre:
   GenreId, Name.

9. InvoiceLine:
   InvoiceId, TrackId, UnitPrice, Quantity.

UNIT AND CALCULATION RULES:

Track.Milliseconds stores duration in milliseconds.

Average track duration in minutes:

AVG(Track.Milliseconds) / 60000.0

Average track duration in seconds:

AVG(Track.Milliseconds) / 1000.0

Individual or total track duration in minutes:

Track.Milliseconds / 60000.0

Do not confuse seconds and minutes.

AGGREGATION RULES:

1. "How many" or "count" means COUNT().
2. "Total", "revenue", or "spending" means SUM().
3. "Average" or "mean" means AVG().
4. "Longest" or "highest" means finding the maximum value.
5. "Each", "per", or "by category" usually requires GROUP BY.
6. For top N results, use ORDER BY and LIMIT.
7. Use the aggregation that directly matches the user's question.

IMPORTANT QUERY EXAMPLES:

Example 1:

Question:
How many tracks are available in each genre?

Correct SQL:
SELECT
    Genre.Name AS GenreName,
    COUNT(Track.TrackId) AS TrackCount
FROM Genre
LEFT JOIN Track ON Genre.GenreId = Track.GenreId
GROUP BY Genre.GenreId, Genre.Name
ORDER BY TrackCount DESC;

Important:
This question asks for a COUNT, not an AVG.

Example 2:

Question:
List the customers from India.

Correct SQL:
SELECT FirstName, LastName
FROM Customer
WHERE Country = 'India';

Important:
Use FirstName and LastName.
Never use a CustomerName column.

Example 3:

Question:
Which customers have the highest total spending?

Correct SQL:
SELECT
    Customer.FirstName,
    Customer.LastName,
    SUM(Invoice.Total) AS TotalSpending
FROM Customer
JOIN Invoice
    ON Customer.CustomerId = Invoice.CustomerId
GROUP BY Customer.CustomerId, Customer.FirstName, Customer.LastName
ORDER BY TotalSpending DESC
LIMIT 5;

Example 4:

Question:
What is the total revenue generated from all invoices?

Correct SQL:
SELECT SUM(Total) AS TotalRevenue
FROM Invoice;

Example 5:

Question:
Find the longest track and show its duration in minutes.

Correct SQL:
SELECT
    Name,
    Milliseconds / 60000.0 AS DurationMinutes
FROM Track
ORDER BY Milliseconds DESC
LIMIT 1;

Example 6:

Question:
What is the average duration of all tracks in minutes?

Example 7:

Question:
Which artist has the most albums?

Correct SQL:
SELECT
    Artist.Name AS ArtistName,
    COUNT(Album.AlbumId) AS AlbumCount
FROM Artist
JOIN Album
    ON Artist.ArtistId = Album.ArtistId
GROUP BY Artist.ArtistId, Artist.Name
ORDER BY AlbumCount DESC
LIMIT 1;

Important:
AlbumId belongs to the Album table, not the Artist table.
Always use COUNT(Album.AlbumId), never COUNT(Artist.AlbumId).

Correct SQL:
SELECT AVG(Milliseconds) / 60000.0 AS AverageDurationMinutes
FROM Track;

Expected result is approximately 6.56 minutes.

OTHER CALCULATION RULES:

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
8. Answer exactly what the user asks. Do not substitute a different calculation.

FINAL VERIFICATION:

- Does the SQL answer the actual question?
- Is the correct aggregation function used?
- Do all tables and columns exist?
- Are all aliases declared?
- Are JOIN conditions valid?
- Are GROUP BY and ORDER BY used correctly?
- Do calculation units match the requested units?

{correction}

USER QUESTION:

{question}

Return only the SQL query.
"""

    response = ask_ollama(prompt)

    sql = clean_sql(response)

    validate_sql(sql)

    return sql
