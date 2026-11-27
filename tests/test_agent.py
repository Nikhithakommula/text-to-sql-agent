
import src.agent.agent as agent


def successful_result(columns=None, rows=None):
    return {
        "success": True,
        "columns": columns if columns is not None else ["CustomerId"],
        "rows": rows if rows is not None else [(1,), (2,)],
        "error": None,
    }


def test_agent_successful_execution(monkeypatch):

    monkeypatch.setattr(
        agent,
        "generate_sql",
        lambda question, error_message=None, schema=None, previous_sql=None: (
            "SELECT COUNT(*) FROM Customer"
        ),
    )

    monkeypatch.setattr(agent, "validate_sql", lambda sql: True)

    monkeypatch.setattr(
        agent,
        "execute_sql",
        lambda sql: successful_result(["Total"], [(59,)])
    )

    result = agent.run_agent("How many customers are there?")

    assert result["success"] is True
    assert result["sql"] == "SELECT COUNT(*) FROM Customer"
    assert result["rows"] == [(59,)]
    assert result["answer"] == "Total: 59"
    assert result["attempts"] == 1
    assert result["error"] is None


def test_agent_retries_after_validation_failure(monkeypatch):

    attempts = {"count": 0}

    def generate(
        question,
        error_message=None,
        schema=None,
        previous_sql=None,
    ):
        attempts["count"] += 1
        return f"SELECT {attempts['count']} FROM Customer"

    def validate(sql):
        if sql == "SELECT 1 FROM Customer":
            raise ValueError("Invalid column")

    monkeypatch.setattr(agent, "generate_sql", generate)
    monkeypatch.setattr(agent, "validate_sql", validate)
    monkeypatch.setattr(
        agent,
        "execute_sql",
        lambda sql: successful_result(["Total"], [(59,)])
    )

    result = agent.run_agent("Test validation retry")

    assert result["success"] is True
    assert result["attempts"] == 2
    assert attempts["count"] == 2


def test_agent_passes_previous_sql_during_retry(monkeypatch):

    received_previous_sql = []

    def generate(
        question,
        error_message=None,
        schema=None,
        previous_sql=None,
    ):
        received_previous_sql.append(previous_sql)

        if len(received_previous_sql) == 1:
            return "SELECT InvalidColumn FROM Customer"

        return "SELECT COUNT(*) FROM Customer"

    def validate(sql):
        if "InvalidColumn" in sql:
            raise ValueError("no such column: InvalidColumn")

        return True

    monkeypatch.setattr(agent, "generate_sql", generate)
    monkeypatch.setattr(agent, "validate_sql", validate)
    monkeypatch.setattr(
        agent,
        "execute_sql",
        lambda sql: successful_result(["Total"], [(59,)])
    )

    result = agent.run_agent("How many customers are there?")

    assert result["success"] is True
    assert result["attempts"] == 2

    assert received_previous_sql == [
        None,
        "SELECT InvalidColumn FROM Customer",
    ]


def test_agent_retries_after_execution_failure(monkeypatch):

    attempts = {"count": 0}

    def generate(
        question,
        error_message=None,
        schema=None,
        previous_sql=None,
    ):
        attempts["count"] += 1
        return f"SELECT {attempts['count']} FROM Customer"

    def execute(sql):
        if sql == "SELECT 1 FROM Customer":
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "error": "Execution error",
            }

        return successful_result(["Total"], [(59,)])

    monkeypatch.setattr(agent, "generate_sql", generate)
    monkeypatch.setattr(agent, "validate_sql", lambda sql: True)
    monkeypatch.setattr(agent, "execute_sql", execute)

    result = agent.run_agent("Test execution retry")

    assert result["success"] is True
    assert result["attempts"] == 2
    assert attempts["count"] == 2


def test_agent_stops_after_max_validation_attempts(monkeypatch):

    attempts = {"count": 0}

    def generate(
        question,
        error_message=None,
        schema=None,
        previous_sql=None,
    ):
        attempts["count"] += 1
        return "SELECT InvalidColumn FROM Customer"

    def validate(sql):
        raise ValueError("Invalid column")

    monkeypatch.setattr(agent, "generate_sql", generate)
    monkeypatch.setattr(agent, "validate_sql", validate)

    result = agent.run_agent("Test maximum validation attempts")

    assert result["success"] is False
    assert result["attempts"] == agent.MAX_ATTEMPTS
    assert attempts["count"] == agent.MAX_ATTEMPTS
    assert "Invalid column" in result["error"]


def test_agent_stops_after_max_execution_attempts(monkeypatch):

    attempts = {"count": 0}

    def generate(
        question,
        error_message=None,
        schema=None,
        previous_sql=None,
    ):
        attempts["count"] += 1
        return "SELECT * FROM Customer"

    def execute(sql):
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "error": "Database execution failed",
        }

    monkeypatch.setattr(agent, "generate_sql", generate)
    monkeypatch.setattr(agent, "validate_sql", lambda sql: True)
    monkeypatch.setattr(agent, "execute_sql", execute)

    result = agent.run_agent("Test maximum execution attempts")

    assert result["success"] is False
    assert result["attempts"] == agent.MAX_ATTEMPTS
    assert attempts["count"] == agent.MAX_ATTEMPTS
    assert "Database execution failed" in result["error"]


def test_format_answer_with_empty_results():

    answer = agent.format_answer(["Name"], [])

    assert answer == "No matching records were found."


def test_format_answer_with_single_value():

    answer = agent.format_answer(["Total"], [(59,)])

    assert answer == "Total: 59"


def test_format_answer_with_multiple_rows():

    columns = ["FirstName", "LastName"]
    rows = [
        ("John", "Smith"),
        ("Mary", "Jones"),
    ]

    answer = agent.format_answer(columns, rows)

    assert "Found 2 result(s)." in answer
    assert "FirstName: John, LastName: Smith" in answer
    assert "FirstName: Mary, LastName: Jones" in answer


def test_format_answer_limits_preview_to_five_rows():

    columns = ["CustomerId"]
    rows = [(1,), (2,), (3,), (4,), (5,), (6,), (7,)]

    answer = agent.format_answer(columns, rows)

    assert "Found 7 result(s)." in answer
    assert "CustomerId: 5" in answer
    assert "CustomerId: 6" not in answer
    assert "... and 2 more result(s)." in answer
