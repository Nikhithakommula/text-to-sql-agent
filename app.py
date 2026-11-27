import streamlit as st

from src.agent.agent import run_agent


st.set_page_config(
    page_title="Text-to-SQL Agent",
    page_icon="🗄️",
    layout="wide",
)


st.title("Text-to-SQL Agent")
st.write(
    "Ask questions about your database in natural language. "
    "The AI agent will generate SQL, validate it, and retrieve results."
)

st.divider()


# Example questions
st.subheader("Example Questions")

examples = [
    "How many customers are there?",
    "Which artist has the most albums?",
    "What is the total revenue generated from all invoices?",
    "Show the top 5 countries based on customer count.",
    "What is the average duration of all tracks in minutes?",
]

for example in examples:
    st.markdown(f"- {example}")


st.divider()


# User question input
st.subheader("Ask Your Question")

with st.form("question_form"):
    question = st.text_input(
        "Enter your database question:",
        placeholder="Example: How many customers are there?",
    )

    submitted = st.form_submit_button(
        "Generate Answer",
        type="primary",
    )


if submitted:
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Agent is processing your question..."):
            try:
                result = run_agent(question.strip())

                st.session_state["agent_result"] = result
                st.session_state["agent_question"] = question.strip()

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")


# Display results
if "agent_result" in st.session_state:
    result = st.session_state["agent_result"]

    st.divider()
    st.subheader("Agent Results")

    st.write(f"**Your Question:** {st.session_state['agent_question']}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Attempts", result["attempts"])

    with col2:
        st.metric(
            "Execution Status",
            "Success" if result["success"] else "Failed",
        )

    if result["sql"]:
        with st.expander("View Generated SQL", expanded=True):
            st.code(result["sql"], language="sql")

    if result["success"]:
        st.success("Query executed successfully.")

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Database Results")

        if result["rows"]:
            table_data = [dict(zip(result["columns"], row)) for row in result["rows"]]

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(f"Total records: {len(result['rows'])}")

        else:
            st.info("No matching records were found.")

    else:
        st.error("Query execution failed.")

        if result["error"]:
            st.write(f"**Error:** {result['error']}")
