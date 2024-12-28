from src.visualization.ternary_plotter import TernaryPlotter
from src.core.question_manager import QuestionManager
from src.data.db_manager import append_record
import streamlit as st
import random

# Initialize question manager and ternary plotter
question_manager = QuestionManager("src/data/questions_responses.json")
plotter = TernaryPlotter(scale=100)

def main():
    # Determine the current page
    if "page" not in st.session_state:
        st.session_state.page = "questions"  # Default page
    if "error_triggered" not in st.session_state:
        st.session_state.error_triggered = False

    if st.session_state.page == "questions":
        display_questions_and_responses()
    elif st.session_state.page == "results":
        display_results_and_chart()

def display_questions_and_responses():
    st.title("Questions and Responses")
    question_keys = question_manager.get_all_question_keys()

    # Ensure error state exists in session state
    if "error_triggered" not in st.session_state:
        st.session_state.error_triggered = False

    has_errors = False  # Track if there are unanswered questions

    for q_key in question_keys:
        question_text = question_manager.get_question_text(q_key)
        responses = question_manager.get_responses(q_key)

        # Shuffle responses once and store in session state
        if f"shuffled_responses_{q_key}" not in st.session_state:
            st.session_state[f"shuffled_responses_{q_key}"] = [
                {"text": "Select an option", "r_value": None}
            ] + random.sample(responses, len(responses))

        shuffled_responses = st.session_state[f"shuffled_responses_{q_key}"]

        # Check if the question has been answered
        is_valid = st.session_state.get(f"{q_key}_r_value") is not None

        # Highlight unanswered questions only after validation
        if not is_valid and st.session_state.error_triggered:
            st.markdown(
                f'<div style="background-color: yellow; padding: 5px; border-radius: 5px; font-weight: bold; font-size: 26px; font-family: Roboto, sans-serif;">{question_text}</div>',
                unsafe_allow_html=True
            )
            has_errors = True
        else:
            st.subheader(question_text)

        # Render radio buttons for the question
        response_r_value = st.radio(
            "",
            options=[r["text"] for r in shuffled_responses],
            index=0 if st.session_state.get(f"{q_key}_r_value") is None else
            [r["text"] for r in shuffled_responses].index(
                next(r["text"] for r in shuffled_responses if r["r_value"] == st.session_state[f"{q_key}_r_value"])
            ),
            key=f"radio_{q_key}",
        )

        # Update session state with the selected response
        selected_response = next((r for r in shuffled_responses if r["text"] == response_r_value), None)
        st.session_state[f"{q_key}_r_value"] = selected_response["r_value"] if selected_response else None

    # Button to validate and navigate
    if st.button("Review Results"):
        # Check if any questions are unanswered
        has_errors = any(
            not st.session_state.get(f"{q_key}_r_value") for q_key in question_keys
        )
        st.session_state.error_triggered = has_errors

        if has_errors:
            # Show error only when the button is clicked
            st.error("Some questions are unanswered. Please scroll up and complete them before proceeding.")
        else:
            # Navigate to results page if no errors
            st.session_state.page = "results"
            st.rerun()

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
            st.rerun()
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
