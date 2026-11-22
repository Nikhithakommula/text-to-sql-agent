from src.sql_generator import generate_sql
from src.sql_executor import execute_sql
from src.sql_validator import validate_sql


MAX_ATTEMPTS = 3


def run_agent(question):

    last_error = None
    sql = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

        try:
            # Step 1: Generate SQL.
            sql = generate_sql(question, last_error)

            print(f"Generated SQL for attempt {attempt}:")
            print(sql)

            # Step 2: Validate SQL.
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

        # Step 3: Execute validated SQL.
        result = execute_sql(sql)

        if result["success"]:
            rows = result["rows"]

            if not rows:
                answer = "No matching records were found."

            elif len(rows) == 1 and len(rows[0]) == 1:
                answer = f"Result: {rows[0][0]}"

            else:
                answer = f"Found {len(rows)} result(s)."

            return {
                "success": True,
                "sql": sql,
                "columns": result["columns"],
                "rows": rows,
                "answer": answer,
                "error": None,
                "attempts": attempt,
            }

        # Step 4: Send execution error for correction.
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
