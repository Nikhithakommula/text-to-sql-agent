from src.agent import run_agent


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
            continue

        print("\nGenerating SQL...")

        result = run_agent(question)

        print("\n" + "-" * 50)

        if result["success"]:

            print("Generated SQL:")
            print(result["sql"])

            print("\nDatabase Result:")

            if result["columns"]:
                print(" | ".join(result["columns"]))

            for row in result["rows"]:
                print(row)

            print("\nAnswer:")
            print(result["answer"])

            print("\nStatus: SUCCESS")

        else:

            print("SQL Generation/Execution Failed:")
            print(result["error"])

            print("\nStatus: FAILED")

        print("-" * 50)


if __name__ == "__main__":
    main()