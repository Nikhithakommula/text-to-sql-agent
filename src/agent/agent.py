from src.sql_generator import generate_sql
from src.sql_executor import execute_sql
from src.sql_validator import validate_sql


MAX_ATTEMPTS = 3
MAX_PREVIEW_ROWS = 5


def format_answer(columns, rows):

    if not rows:
        return "No matching records were found."

    if len(rows) == 1 and len(rows[0]) == 1:
        return f"{columns[0]}: {rows[0][0]}"

    answer_lines = [f"Found {len(rows)} result(s).", "Results:"]

    preview_rows = rows[:MAX_PREVIEW_ROWS]

    for row in preview_rows:
        record = ", ".join(f"{column}: {value}" for column, value in zip(columns, row))

        answer_lines.append(record)

    if len(rows) > MAX_PREVIEW_ROWS:
        answer_lines.append(f"... and {len(rows) - MAX_PREVIEW_ROWS} more result(s).")

    return "\n".join(answer_lines)


def run_agent(question):

    last_error = None
    sql = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

        try:
            sql = generate_sql(question, last_error)

            print(f"Generated SQL for attempt {attempt}:")
            print(sql)

            validate_sql(sql)

        except Exception as e:
            last_error = (
                f"Previous SQL:\n{sql}\n\n"
                f"Validation error:\n{str(e)}\n\n"
                "Generate a corrected query. "
                "Check that every table alias is declared "
                "in the FROM or JOIN clause before using it."
            )

            print(f"Attempt {attempt} failed: {str(e)}")

            continue

        result = execute_sql(sql)

        if result["success"]:
            rows = result["rows"]
            columns = result["columns"]

            answer = format_answer(columns, rows)

            return {
                "success": True,
                "sql": sql,
                "columns": columns,
                "rows": rows,
                "answer": answer,
                "error": None,
                "attempts": attempt,
            }

        last_error = (
            f"Previous SQL:\n{sql}\n\n"
            f"Execution error:\n{result['error']}\n\n"
            "Generate a corrected query."
        )

        print(f"Attempt {attempt} failed: {result['error']}")

    return {
        "success": False,
        "sql": sql,
        "columns": [],
        "rows": [],
        "answer": None,
        "error": last_error,
        "attempts": MAX_ATTEMPTS,
    }
