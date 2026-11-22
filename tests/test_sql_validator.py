import pytest

from src.sql_validator import validate_sql


def test_valid_select_query():
    assert validate_sql("SELECT * FROM Customer") is True


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO Customer (FirstName) VALUES ('Test')",
        "UPDATE Customer SET FirstName = 'Test'",
        "DELETE FROM Customer",
        "DROP TABLE Customer",
        "CREATE TABLE Test (id INTEGER)",
        "ALTER TABLE Customer ADD COLUMN TestColumn TEXT",
    ],
)
def test_unsafe_queries_are_rejected(sql):
    with pytest.raises(ValueError):
        validate_sql(sql)


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("")


def test_invalid_sql_syntax_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("SELECT FROM Customer")


def test_multiple_statements_are_rejected():
    with pytest.raises(ValueError):
        validate_sql("SELECT * FROM Customer; SELECT * FROM Artist")


def test_nonexistent_table_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("SELECT * FROM UnknownTable")
