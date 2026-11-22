from src.agent import run_agent


def display_table(columns, rows):

    if not columns or not rows:
        print("No records to display.")
        return

    widths = []

    for index, column in enumerate(columns):
        values = [str(row[index]) for row in rows]

        width = max(len(str(column)), max(len(value) for value in values))

        widths.append(width)

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    header = (
        "| "
        + " | ".join(
            str(column).ljust(widths[index]) for index, column in enumerate(columns)
        )
        + " |"
    )

    print(separator)
    print(header)
    print(separator)

    for row in rows:
        formatted_row = (
            "| "
            + " | ".join(
                str(value).ljust(widths[index]) for index, value in enumerate(row)
            )
            + " |"
        )

        print(formatted_row)

    print(separator)
    print(f"Total records: {len(rows)}")


def main():

    print()
    print("=" * 50)
    print("              TEXT-TO-SQL AGENT")
    print("=" * 50)

    while True:
        question = input("\nAsk your question: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("\nGoodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        print("\nGenerating SQL...")

        result = run_agent(question)

        print("\n" + "-" * 50)

        if result["success"]:
            print("Generated SQL:")
            print(result["sql"])

            print("\nDatabase Result:")

            display_table(result["columns"], result["rows"])

            print("\nAnswer:")
            print(result["answer"])

            print("\nStatus: SUCCESS")
            print("Attempts:", result["attempts"])

        else:
            print("SQL Generation/Execution Failed:")
            print(result["error"])

            print("\nStatus: FAILED")
            print("Attempts:", result["attempts"])

        print("-" * 50)


if __name__ == "__main__":
    main()
