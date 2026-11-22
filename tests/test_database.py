from sqlalchemy import inspect

from src.database.connection import engine


EXPECTED_TABLES = {
    "Album",
    "Artist",
    "Customer",
    "Employee",
    "Genre",
    "Invoice",
    "InvoiceLine",
    "MediaType",
    "Playlist",
    "PlaylistTrack",
    "Track",
}


def test_database_connection():
    database_inspector = inspect(engine)

    tables = database_inspector.get_table_names()

    assert len(tables) > 0


def test_expected_tables_exist():
    database_inspector = inspect(engine)

    actual_tables = set(database_inspector.get_table_names())

    assert EXPECTED_TABLES.issubset(actual_tables)


def test_database_has_eleven_tables():
    database_inspector = inspect(engine)

    tables = database_inspector.get_table_names()

    assert len(tables) == 11


def test_customer_table_columns():
    database_inspector = inspect(engine)

    columns = {column["name"] for column in database_inspector.get_columns("Customer")}

    expected_columns = {
        "CustomerId",
        "FirstName",
        "LastName",
        "Country",
    }

    assert expected_columns.issubset(columns)


def test_track_table_columns():
    database_inspector = inspect(engine)

    columns = {column["name"] for column in database_inspector.get_columns("Track")}

    expected_columns = {
        "TrackId",
        "Name",
        "GenreId",
        "Milliseconds",
    }

    assert expected_columns.issubset(columns)


def test_invoice_table_columns():
    database_inspector = inspect(engine)

    columns = {column["name"] for column in database_inspector.get_columns("Invoice")}

    expected_columns = {
        "InvoiceId",
        "CustomerId",
        "Total",
        "InvoiceDate",
    }

    assert expected_columns.issubset(columns)
