import streamlit as st
import sys
from pathlib import Path
import logging
import time

# Configure logging
logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add src directory to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from questions.question_manager import QuestionManager
from data.data_handler import DataHandler
from visualization.report import SurveyReport

def main():
    start_time = time.time()
    st.title("Worldview Survey")

    # Initialize components
    question_manager = QuestionManager()
    data_handler = DataHandler()
    report = SurveyReport()

    # Track responses
    user_responses = {}
    user_scores = []
    warning_placeholders = {}

    # Define the form
    with st.form(key='survey_form'):
        # Display questions
        for q_key in question_manager.get_all_question_keys():
            st.subheader(question_manager.get_question_text(q_key))

            # Initialize a placeholder for the warning message below the question
            warning_placeholders[q_key] = st.empty()

            # Get randomized options
            options = question_manager.get_randomized_options(q_key, st.session_state)
            option_texts = [opt["text"] for opt in options]
            option_texts.insert(0, "Select an option from the list below to proceed.")

            # Display radio button
            user_choice = st.radio("", option_texts, key=f"radio_{q_key}")

            # Store the user's choice
            user_responses[q_key] = user_choice

        # Submit button
        submit_button = st.form_submit_button(label='Submit')

    # Post-form submission processing
    if submit_button:
        all_questions_answered = True

        # Validate responses
        for q_key, user_choice in user_responses.items():
            if user_choice == "Select an option from the list below to proceed.":
                warning_placeholders[q_key].warning("⚠️ Please select an option for this question.")
                all_questions_answered = False
            else:
                warning_placeholders[q_key].empty()  # Clear any existing warning
                for opt in options:
                    if opt["text"] == user_choice:
                        user_scores.append(opt["scores"])
                        break

        if all_questions_answered:
            if question_manager.validate_responses(user_responses, user_scores):
                avg_score = data_handler.calculate_average_score(user_scores)
                data_handler.save_response(user_responses, user_scores)

                # Serialize data into query parameters
                user_scores_str = [','.join(map(str, score)) for score in user_scores]
                avg_score_str = ','.join(map(str, avg_score))
                results_url = f"/results_page?user_scores={','.join(user_scores_str)}&avg_score={avg_score_str}"

                # Provide a link to open the results in a new window
                st.markdown(
                    f'<a href="{results_url}" target="_blank" style="color: white; background-color: green; padding: 10px; text-decoration: none;">'
                    f'View Results in a New Window</a>',
                    unsafe_allow_html=True
                )
            else:
                st.error("Invalid response data. Please try again.")
        else:
            st.error("⚠️ Please answer all questions before submitting!")

    # Footer
    st.write("Your responses are saved anonymously and will be used for research purposes.")
    end_time = time.time()

    # Debugging information
    st.write(f"Total page load time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
