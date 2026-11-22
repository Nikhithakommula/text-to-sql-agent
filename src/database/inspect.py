from sqlalchemy import inspect

from src.database.connection import engine


def show_tables():
    database_inspector = inspect(engine)

    tables = database_inspector.get_table_names()

    print("Tables in the database:")

    for table in tables:
        print("-", table)


def show_columns(table_name):
    database_inspector = inspect(engine)

    columns = database_inspector.get_columns(table_name)

    print(f"\nColumns in {table_name}:")

    for column in columns:
        print("-", column["name"], "|", column["type"])


if __name__ == "__main__":
    show_tables()
    show_columns("Customer")