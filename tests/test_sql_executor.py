import pytest

from src.sql_executor import execute_sql


def test_valid_select_query():
    result = execute_sql("SELECT * FROM Customer LIMIT 5")

    assert result["success"] is True
    assert len(result["rows"]) == 5
    assert "CustomerId" in result["columns"]


def test_count_query():
    result = execute_sql("SELECT COUNT(*) AS total FROM Customer")

    assert result["success"] is True
    assert result["rows"][0][0] == 59


def test_query_returns_column_names():
    result = execute_sql("SELECT FirstName, LastName FROM Customer LIMIT 1")

    assert result["success"] is True
    assert result["columns"] == ["FirstName", "LastName"]


def test_empty_query_is_rejected():
    result = execute_sql("")

    assert result["success"] is False
    assert "Only SELECT queries are allowed" in result["error"]


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO Customer (FirstName) VALUES ('Test')",
        "UPDATE Customer SET FirstName = 'Test'",
        "DELETE FROM Customer",
    ],
)
def test_modification_queries_are_rejected(sql):
    result = execute_sql(sql)

    assert result["success"] is False


def test_multiple_statements_are_rejected():
    result = execute_sql("SELECT * FROM Customer; SELECT * FROM Artist")

    assert result["success"] is False
    assert "Multiple SQL statements" in result["error"]


def test_invalid_table_is_rejected():
    result = execute_sql("SELECT * FROM UnknownTable")

    assert result["success"] is False
    assert result["error"] is not None


def test_no_matching_records():
    result = execute_sql("SELECT * FROM Customer WHERE Country = 'UnknownCountry'")

    assert result["success"] is True
    assert result["rows"] == []
