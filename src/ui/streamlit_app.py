from src.core.question_manager import QuestionManager
from src.data.db_manager import initialize_database, append_record  # Import database functions
from src.visualization.ternary_plotter import TernaryPlotter  # Import TernaryPlotter
import streamlit as st

# Initialize database at app startup
initialize_database()

question_manager = QuestionManager("src/data/questions_responses.json")

def main():
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    if st.session_state.page == "welcome":
        display_welcome_page()
    elif st.session_state.page == "question":
        display_question_page()
    elif st.session_state.page == "review":
        display_review_page()

def display_welcome_page():
    st.title("Welcome to the Worldview Survey")
    st.write("Lorem Ipsum text explaining the survey. Click below to start.")
    if st.button("Start Survey"):
        st.session_state.page = "question"
        st.rerun()

def display_question_page():
    # Ensure current_question_index is initialized
    if "current_question_index" not in st.session_state:
        st.session_state["current_question_index"] = 0

    current_idx = st.session_state["current_question_index"]
    question_keys = question_manager.get_all_question_keys()

    # Prevent out-of-range access
    if current_idx >= len(question_keys):
        st.session_state.page = "review"  # Transition to review page
        st.rerun()

    q_key = question_keys[current_idx]  # Safe access after boundary check
    question_text = question_manager.get_question_text(q_key)
    options = question_manager.get_randomized_responses(q_key, st.session_state)

    # Display the question
    st.header(question_text)
    selected_option = st.radio(
        "Select an option:",
        options,
        format_func=lambda x: x["text"],  # Display the text of each response
        index=next(
            (i for i, opt in enumerate(options) if opt["text"] == st.session_state.get(f"{q_key}_answer", {}).get("text", "Please select a response")),
            0
        ),
        key=f"{q_key}_selection"
    )

    if selected_option["text"] != "Please select a response":
        st.session_state[f"{q_key}_answer"] = selected_option
        st.session_state[f"{q_key}_r_value"] = selected_option["r_value"]

    # Navigation Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            if current_idx > 0:
                st.session_state["current_question_index"] -= 1
            else:
                st.session_state.page = "welcome"
            st.rerun()
    with col2:
        if st.button("Next"):
            if selected_option["text"] == "Please select a response":
                st.error("Please select a valid response to proceed.")
            else:
                st.session_state["current_question_index"] += 1
                st.rerun()

def display_review_page():
    from src.visualization.ternary_plotter import TernaryPlotter
    plotter = TernaryPlotter(scale=100)

    st.title("Your Aggregate Results")
    question_keys = question_manager.get_all_question_keys()

    responses = {}
    individual_scores = []  # Store individual scores
    n1, n2, n3 = 0, 0, 0  # Initialize aggregate scores

    for q_key in question_keys:
        question_text = question_manager.get_question_text(q_key)
        response_r_value = st.session_state.get(f"{q_key}_r_value", None)

        if response_r_value is not None:
            response = question_manager.get_responses(q_key)
            selected_response = next((r for r in response if r["r_value"] == response_r_value), None)
            if selected_response:
                response_text = selected_response["text"]
                scores = selected_response["scores"]
                individual_scores.append(scores)
                n1 += scores[0]
                n2 += scores[1]
                n3 += scores[2]
            else:
                response_text = "No valid response found."
        else:
            response_text = "No response"

        responses[q_key] = response_text

    # Normalize aggregated scores for ternary plot
    total = n1 + n2 + n3
    avg_score = [n1 / total * 100, n2 / total * 100, n3 / total * 100] if total > 0 else None

    # Ternary Plot Display at the Top
    if individual_scores and avg_score:
        chart = plotter.create_plot(user_scores=individual_scores, avg_score=avg_score)
        plotter.display_plot(chart)
    else:
        st.write("No sufficient data to generate a ternary chart.")

    # Display Individual Responses
    st.header("Review Your Responses")
    for q_key in question_keys:
        question_text = question_manager.get_question_text(q_key)
        response_r_value = st.session_state.get(f"{q_key}_r_value", None)

        if response_r_value is not None:
            response = question_manager.get_responses(q_key)
            selected_response = next((r for r in response if r["r_value"] == response_r_value), None)
            if selected_response:
                response_text = selected_response["text"]
            else:
                response_text = "No valid response found."
        else:
            response_text = "No response"

        st.subheader(question_text)
        st.write(f"Your Answer: {response_text}")

    # Navigation Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.page = "question"
            st.session_state.current_question_index = len(question_keys) - 1
            st.rerun()
    with col2:
        if st.button("Submit"):
            append_record(
                q1=responses["Q1"], q2=responses["Q2"], q3=responses["Q3"],
                q4=responses["Q4"], q5=responses["Q5"], q6=responses["Q6"],
                n1=n1, n2=n2, n3=n3,
                plot_x=n2 / total * 100 if total > 0 else 0,
                plot_y=n3 / total * 100 if total > 0 else 0,
                session_id="test_session"
            )
            st.success("Thank you for completing the survey! Your responses have been recorded.")


# Placeholder aggregate functions
def calculate_aggregates(responses):
    # Replace this with actual logic
    return 10, 20, 30

def calculate_plot_coordinates(n1, n2, n3):
    # Replace this with actual logic
    return 12.34, 56.78

if __name__ == "__main__":
    main()
