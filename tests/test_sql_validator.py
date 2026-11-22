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


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * INTO NewTable FROM Customer",
        "PRAGMA table_info(Customer)",
        "ATTACH DATABASE 'test.db' AS test",
        "DETACH DATABASE test",
    ],
)
def test_additional_unsafe_queries_are_rejected(sql):
    with pytest.raises(ValueError):
        validate_sql(sql)


def test_select_with_join_is_allowed():
    sql = """
        SELECT Customer.FirstName, Invoice.Total
        FROM Customer
        JOIN Invoice ON Customer.CustomerId = Invoice.CustomerId
    """

    assert validate_sql(sql) is True


def test_select_with_group_by_is_allowed():
    sql = """
        SELECT Country, COUNT(*)
        FROM Customer
        GROUP BY Country
    """

    assert validate_sql(sql) is True
