import os
from sqlalchemy import create_engine, text


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "Chinook.sqlite")

engine = create_engine(f"sqlite:///{DATABASE_PATH}")


def execute_sql(sql):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql))

            rows = result.fetchall()

            columns = list(result.keys())

        return {
            "success": True,
            "columns": columns,
            "rows": [tuple(row) for row in rows],
            "error": None,
        }

    except Exception as e:
        return {"success": False, "columns": [], "rows": [], "error": str(e)}
