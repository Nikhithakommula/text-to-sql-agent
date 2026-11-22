import sqlglot
from sqlglot import exp

from src.sql_executor import engine


def validate_sql(sql):
    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as e:
        raise ValueError(f"SQL syntax error: {str(e)}")

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    parsed = statements[0]

    if not isinstance(parsed, (exp.Select, exp.Subquery, exp.Union)):
        raise ValueError("Only SELECT queries are allowed.")

    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
    )

    for node in parsed.walk():
        if isinstance(node, forbidden):
            raise ValueError("Unsafe SQL operation detected.")

    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA query_only = ON")
            connection.exec_driver_sql(f"EXPLAIN QUERY PLAN {sql}").fetchall()

    except Exception as e:
        raise ValueError(f"Database schema or query validation failed: {str(e)}")

    return True
