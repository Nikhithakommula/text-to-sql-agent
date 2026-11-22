from src.sql_generator import generate_sql
from src.sql_executor import execute_sql


def run_agent(question):

    last_error = None

    for attempt in range(3):
        try:
            sql = generate_sql(question, last_error)

        except Exception as e:
            return {
                "success": False,
                "sql": None,
                "columns": [],
                "rows": [],
                "answer": None,
                "error": str(e),
            }

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
            }

        last_error = result["error"]

    return {
        "success": False,
        "sql": sql,
        "columns": [],
        "rows": [],
        "answer": None,
        "error": last_error,
    }
