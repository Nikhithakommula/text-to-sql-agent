import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.sql_generator import generate_sql, get_database_schema
from src.sql_executor import execute_sql
from src.sql_validator import validate_sql


MAX_ATTEMPTS = 3
MAX_PREVIEW_ROWS = 5


class AgentState(TypedDict, total=False):
    question: str
    schema: str
    sql: str
    error: str
    attempts: int
    columns: list
    rows: list
    answer: str
    success: bool
    valid: bool


def retrieve_schema_node(state: AgentState):

    print("\nRetrieving database schema...")

    try:
        schema = get_database_schema()

        return {
            "schema": schema,
            "error": None,
        }

    except Exception as e:
        return {
            "error": f"Schema retrieval failed: {str(e)}",
            "success": False,
        }


def generate_query_node(state: AgentState):

    attempt = state.get("attempts", 0) + 1

    print(f"\nAttempt {attempt}/{MAX_ATTEMPTS}")

    try:
        sql = generate_sql(
            state["question"],
            state.get("error"),
            state["schema"],
        )

        if not sql:
            raise ValueError("SQL generation returned an empty query.")

        print("Generated SQL:")
        print(sql)

        return {
            "sql": sql,
            "attempts": attempt,
            "error": None,
            "valid": False,
        }

    except Exception as e:
        error = f"SQL generation failed: {str(e)}"
        print(error)

        return {
            "sql": None,
            "attempts": attempt,
            "error": error,
            "success": False,
            "valid": False,
        }


def validate_query_node(state: AgentState):

    try:
        validate_sql(state["sql"])

        print("SQL validation successful.")

        return {
            "valid": True,
            "error": None,
        }

    except Exception as e:
        error = f"SQL validation failed: {str(e)}"
        print(error)

        return {
            "valid": False,
            "error": error,
            "success": False,
        }


def execute_query_node(state: AgentState):

    try:
        result = execute_sql(state["sql"])

        if not result["success"]:
            error = result.get("error") or "SQL execution failed."

            print(f"SQL execution failed: {error}")

            return {
                "success": False,
                "columns": [],
                "rows": [],
                "error": error,
            }

        print("SQL execution successful.")

        return {
            "success": True,
            "columns": result["columns"],
            "rows": result["rows"],
            "error": None,
        }

    except Exception as e:
        error = f"SQL execution failed: {str(e)}"
        print(error)

        return {
            "success": False,
            "columns": [],
            "rows": [],
            "error": error,
        }


def format_value(value):

    if isinstance(value, float):
        return f"{value:.2f}"

    return str(value)


def format_single_value(column, value):

    units = {
        "Minutes": "minutes",
        "Seconds": "seconds",
        "Hours": "hours",
    }

    for suffix, unit in units.items():
        if column.endswith(suffix):
            label = column[: -len(suffix)]

            label = re.sub(
                r"([a-z0-9])([A-Z])",
                r"\1 \2",
                label,
            )

            return f"{label}: {format_value(value)} {unit}"

    return f"{column}: {format_value(value)}"


def format_answer(columns, rows):

    if not rows:
        return "No matching records were found."

    if len(rows) == 1 and len(rows[0]) == 1:
        return format_single_value(columns[0], rows[0][0])

    answer = [f"Found {len(rows)} result(s)."]

    for row in rows[:MAX_PREVIEW_ROWS]:
        row_data = ", ".join(
            f"{column}: {format_value(value)}" for column, value in zip(columns, row)
        )

        answer.append(row_data)

    if len(rows) > MAX_PREVIEW_ROWS:
        remaining = len(rows) - MAX_PREVIEW_ROWS
        answer.append(f"... and {remaining} more result(s).")

    return "\n".join(answer)


def format_answer_node(state: AgentState):

    answer = format_answer(
        state["columns"],
        state["rows"],
    )

    return {
        "answer": answer,
        "success": True,
    }


def route_after_schema(state: AgentState):

    if state.get("error"):
        return "end"

    return "generate"


def route_after_generation(state: AgentState):

    if state.get("error"):
        if state["attempts"] < MAX_ATTEMPTS:
            return "retry"

        return "end"

    return "validate"


def route_after_validation(state: AgentState):

    if state.get("valid"):
        return "execute"

    if state["attempts"] < MAX_ATTEMPTS:
        return "retry"

    return "end"


def route_after_execution(state: AgentState):

    if state.get("success"):
        return "format"

    if state["attempts"] < MAX_ATTEMPTS:
        return "retry"

    return "end"


def build_agent_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve_schema", retrieve_schema_node)
    workflow.add_node("generate_query", generate_query_node)
    workflow.add_node("validate_query", validate_query_node)
    workflow.add_node("execute_query", execute_query_node)
    workflow.add_node("format_answer", format_answer_node)

    workflow.add_edge(START, "retrieve_schema")

    workflow.add_conditional_edges(
        "retrieve_schema",
        route_after_schema,
        {
            "generate": "generate_query",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "generate_query",
        route_after_generation,
        {
            "validate": "validate_query",
            "retry": "generate_query",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "validate_query",
        route_after_validation,
        {
            "execute": "execute_query",
            "retry": "generate_query",
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "execute_query",
        route_after_execution,
        {
            "format": "format_answer",
            "retry": "generate_query",
            "end": END,
        },
    )

    workflow.add_edge("format_answer", END)

    return workflow.compile()


agent_graph = build_agent_graph()


def run_agent(question):

    initial_state = {
        "question": question,
        "schema": "",
        "sql": None,
        "error": None,
        "attempts": 0,
        "columns": [],
        "rows": [],
        "answer": None,
        "success": False,
        "valid": False,
    }

    final_state = agent_graph.invoke(initial_state)

    return {
        "success": final_state.get("success", False),
        "sql": final_state.get("sql"),
        "columns": final_state.get("columns", []),
        "rows": final_state.get("rows", []),
        "answer": final_state.get("answer"),
        "attempts": final_state.get("attempts", 0),
        "error": final_state.get("error"),
    }
