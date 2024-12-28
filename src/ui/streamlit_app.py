from src.visualization.ternary_plotter import TernaryPlotter
from src.core.question_manager import QuestionManager
from src.data.db_manager import append_record
import streamlit as st
import random

# Initialize question manager
question_manager = QuestionManager("src/data/questions_responses.json")

# Initialize ternary plotter
plotter = TernaryPlotter(scale=100)


def main():
    # Determine the current page state
    if "page" not in st.session_state:
        st.session_state.page = "questions"  # Default page

    # Navigate between pages
    if st.session_state.page == "questions":
        display_questions_and_responses()
    elif st.session_state.page == "results":
        display_results_and_chart()


def display_questions_and_responses():
    st.title("Questions and Responses")
    question_keys = question_manager.get_all_question_keys()

    for q_key in question_keys:
        question_text = question_manager.get_question_text(q_key)
        responses = question_manager.get_responses(q_key)

        # Randomize responses (excluding the placeholder)
        if f"{q_key}_shuffled_responses" not in st.session_state:
            randomized_responses = random.sample(responses, len(responses))
            st.session_state[f"{q_key}_shuffled_responses"] = [{"text": "Select an option", "r_value": None}] + randomized_responses
        shuffled_responses = st.session_state[f"{q_key}_shuffled_responses"]

        # Generate a unique key for the question
        key = f"radio_{q_key}"

        st.subheader(question_text)

        # Initialize session state if not already set
        if f"{q_key}_r_value" not in st.session_state:
            st.session_state[f"{q_key}_r_value"] = None

        # Display the radio button for responses
        response_r_value = st.radio(
            "Select your response:",
            options=[r["text"] for r in shuffled_responses],
            index=0 if st.session_state[f"{q_key}_r_value"] is None else
            [r["text"] for r in shuffled_responses].index(
                next(r["text"] for r in shuffled_responses if r["r_value"] == st.session_state[f"{q_key}_r_value"])
            ),
            key=key  # Use unique key for the question
        )

        # Update session state with the selected response
        selected_response = next(r for r in shuffled_responses if r["text"] == response_r_value)
        st.session_state[f"{q_key}_r_value"] = selected_response["r_value"]

    # Add navigation to results
    if st.button("Review Results"):
        st.session_state.page = "results"  # Navigate to the results page
        st.query_params = {"page": "results"}  # Update query parameters
        st.rerun()  # Force app re-run


def display_results_and_chart():
    st.title("Your Aggregate Results")
    question_keys = question_manager.get_all_question_keys()

    responses_summary = {}
    individual_scores = []  # Store individual scores
    n1, n2, n3 = 0, 0, 0  # Initialize aggregate scores

    for q_key in question_keys:
        question_text = question_manager.get_question_text(q_key)
        response_r_value = st.session_state.get(f"{q_key}_r_value", None)
        responses = question_manager.get_responses(q_key)

        if response_r_value is not None:
            selected_response = next((r for r in responses if r["r_value"] == response_r_value), None)
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
            response_text = "No response selected."

        # Add the response to the summary
        responses_summary[q_key] = (question_text, response_text)

    # Normalize aggregated scores for ternary plot
    total = n1 + n2 + n3
    avg_score = [n1 / total * 100, n2 / total * 100, n3 / total * 100] if total > 0 else None

    # Display ternary plot
    if individual_scores and avg_score:
        chart = plotter.create_plot(user_scores=individual_scores, avg_score=avg_score)
        plotter.display_plot(chart)
    else:
        st.write("No sufficient data to generate a ternary chart.")

    st.header("Review Your Responses")
    for q_key, (question_text, response_text) in responses_summary.items():
        st.subheader(question_text)
        st.write(f"▶ {response_text}")

    # Add navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Questions"):
            st.session_state.page = "questions"
            st.query_params = {"page": "questions"}  # Update query parameters
            st.rerun()  # Force app re-run
    with col2:
        if st.button("Submit Survey"):
            append_record(
                q1=responses_summary.get("Q1", ("", "No response"))[1],
                q2=responses_summary.get("Q2", ("", "No response"))[1],
                q3=responses_summary.get("Q3", ("", "No response"))[1],
                q4=responses_summary.get("Q4", ("", "No response"))[1],
                q5=responses_summary.get("Q5", ("", "No response"))[1],
                q6=responses_summary.get("Q6", ("", "No response"))[1],
                n1=n1, n2=n2, n3=n3,
                plot_x=n2 / total * 100 if total > 0 else 0,
                plot_y=n3 / total * 100 if total > 0 else 0,
                session_id="test_session"
            )
            st.success("Thank you for completing the survey! Your responses have been recorded.")


if __name__ == "__main__":
    main()
