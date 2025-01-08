# src/ui/streamlit_app.py
import sqlite3
from pathlib import Path  # Add this for better path handling
import streamlit as st
import platform 
import random
import os
import uuid
import json # Add this for JSON logging
from src.visualization.ternary_plotter import TernaryPlotter
from src.core.question_manager import QuestionManager
from src.data.db_manager import append_record
from src.visualization.worldview_results import display_results_page
from version import __version__
from datetime import datetime
import logging
import pandas as pd
import sys

# Set up logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
db_path = str(Path(__file__).parent.parent / "data" / "survey_results.db")
logger.debug(f"DB Path: {db_path}")
logger.debug(f"Database Exists: {os.path.exists(db_path)}")

def log_table_contents():
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.debug(f"Tables in database: {tables}")
            
            # Log contents of the first table
            if tables:
                first_table = tables[0][0]
                cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                records = cursor.fetchall()
                logger.debug(f"Contents of {first_table}: {records}")
    except Exception as e:
        logger.error(f"Error logging table contents: {e}", exc_info=True)

def get_browser_info():
    """Get basic system information as a browser placeholder"""
    try:
        return platform.system()  # Returns 'Windows', 'Linux', 'Darwin' etc.
    except:
        return "Unknown System"

def get_region_info():
    """Get basic region information"""
    try:
        return platform.node()  # Returns computer's network name
    except:
        return "Unknown Region"

# Initialize question manager and ternary plotter
question_manager = QuestionManager("src/data/questions_responses.json")
plotter = TernaryPlotter(scale=100)

def initialize_session():
    """Initialize session state with a unique session ID if not already present"""
    if 'session_id' not in st.session_state:
        # Create a unique session ID combining timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]  # Take first 8 characters of UUID
        st.session_state.session_id = f"{timestamp}_{unique_id}"

def get_environment_source():
    """Determine if we're running locally or on server"""
    cwd = os.getcwd()
    logger.debug(f"BEGIN ENVIRONMENT CHECK ---------------")
    logger.debug(f"Current working directory: {cwd}")
    
    # Add detailed checks
    env_details = {
        'cwd': cwd,
        'mount_exists': os.path.exists('/mount/src'),
        'in_path': '/mount/src' in cwd,
        'full_path': os.path.abspath(cwd)
    }
    logger.debug(f"Environment details: {env_details}")
    
    # Check if we're in production
    is_production = '/mount/src' in cwd
    source = 'server' if is_production else 'local'
    
    logger.debug(f"Environment Check - Is Production: {is_production}")
    logger.debug(f"Environment Check - Determined Source: {source}")
    logger.debug(f"END ENVIRONMENT CHECK -----------------")
    
    return source

def calculate_n_values(session_state):
    """Calculate N values from response scores"""
    total_scores = [0, 0, 0]  # [PreModern, Modern, PostModern]
    question_keys = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6']
    
    for q_key in question_keys:
        response_r_value = session_state.get(f"{q_key}_r_value")
        if response_r_value is not None:
            responses = question_manager.get_responses(q_key)
            selected_response = next((r for r in responses if r["r_value"] == response_r_value), None)
            if selected_response:
                scores = selected_response["scores"]
                total_scores = [a + b for a, b in zip(total_scores, scores)]
    
    # Convert to percentages
    total = sum(total_scores)
    if total > 0:
        n1 = int((total_scores[0] / total) * 100)
        n2 = int((total_scores[1] / total) * 100)
        n3 = int((total_scores[2] / total) * 100)
        return n1, n2, n3
    return 0, 0, 0

def calculate_plot_coordinates(n1, n2, n3):
    """Calculate plot coordinates from N values"""
    total = n1 + n2 + n3
    if total > 0:
        plot_x = (2 * n3 + n1) / (2 * total)
        plot_y = n1 / total
        return float(plot_x), float(plot_y)
    return 0.0, 0.0

def save_survey_results(session_state):
    """Save survey results to the database and verify by fetching updated records."""
    with st.expander("💾 Database Operation Details", expanded=True):
        # Prepare data for saving
        q1_value = session_state.get('Q1_r_value')
        q2_value = session_state.get('Q2_r_value')
        q3_value = session_state.get('Q3_r_value')
        q4_value = session_state.get('Q4_r_value')
        q5_value = session_state.get('Q5_r_value')
        q6_value = session_state.get('Q6_r_value')

        n1, n2, n3 = calculate_n_values(session_state)
        plot_x, plot_y = calculate_plot_coordinates(n1, n2, n3)

        source = get_environment_source()
        browser = get_browser_info()
        region = get_region_info()

        # Save to database
        try:
            append_record(
                q1=q1_value, q2=q2_value, q3=q3_value, q4=q4_value,
                q5=q5_value, q6=q6_value, n1=n1, n2=n2, n3=n3,
                plot_x=plot_x, plot_y=plot_y, session_id=session_state.session_id,
                hash_email_session=None, browser=browser, region=region,
                source=source, version=__version__
            )

            # Read the latest data from the database
            with sqlite3.connect(db_path) as conn:
                updated_table = pd.read_sql_query("SELECT * FROM survey_results ORDER BY timestamp DESC", conn)
                st.success(f"✅ Save successful! Records updated.")
                st.write("### Updated Table:")
                st.dataframe(updated_table)

        except Exception as e:
            st.error("❌ Save Failed!")
            st.error(f"Error: {e}")

    # Display persistent debug info at the bottom of the page
    st.markdown("---")
    st.subheader("📊 Database Operation Summary")
    if 'debug_info' in st.session_state:
        with st.expander("View Complete Debug Information", expanded=True):
            st.json(st.session_state.debug_info)

def display_questions_and_responses():
    # Debug: Check initial state
    # print("\n=== Entering display_questions_and_responses() ===")
    # print("Query params:", st.query_params)
    # print("Current session state keys:", list(st.session_state.keys()))
    
    # Force scroll to top on initialization
    if 'init' not in st.query_params:
    #    print("No init param found - adding it")
        st.query_params['init'] = '1'
    #    print("Added init param, about to rerun")
        st.rerun()
    else:
        print("Init param present:", st.query_params['init'])

    st.title("Modernity Worldview Survey")
    question_keys = question_manager.get_all_question_keys()
    #print("Loaded question keys:", question_keys)

    # Initialise validation state if not exists
    if "validation_attempted" not in st.session_state:
        #print("Initialising validation_attempted state")
        st.session_state.validation_attempted = False

    # Display questions
    for q_key in question_keys:
        #print(f"\nProcessing question {q_key}")
        question_text = question_manager.get_question_text(q_key)
        responses = question_manager.get_responses(q_key)

        # Initialise shuffled responses
        if f"shuffled_responses_{q_key}" not in st.session_state:
            #print(f"Initialising shuffled responses for {q_key}")
            st.session_state[f"shuffled_responses_{q_key}"] = [
                {"text": "Select an option", "r_value": None}
            ] + random.sample(responses, len(responses))

        shuffled_responses = st.session_state[f"shuffled_responses_{q_key}"]

        # Check if question is answered
        is_answered = st.session_state.get(f"{q_key}_r_value") is not None
        #print(f"Question {q_key} answered status:", is_answered)

        # Apply highlighting if validation was attempted and question is unanswered
        if st.session_state.validation_attempted and not is_answered:
            #print(f"Highlighting unanswered question {q_key}")
            st.markdown(
                f'<div style="background-color: yellow; padding: 5px; border-radius: 5px; font-weight: bold; font-size: 26px; font-family: Roboto, sans-serif;">{question_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.subheader(question_text)

        # Render radio buttons
        response_r_value = st.radio(
            "",
            options=[r["text"] for r in shuffled_responses],
            index=0 if st.session_state.get(f"{q_key}_r_value") is None else
            [r["text"] for r in shuffled_responses].index(
                next(r["text"] for r in shuffled_responses if r["r_value"] == st.session_state[f"{q_key}_r_value"])
            ),
            key=f"radio_{q_key}",
        )

        # Update session state with selection
        selected_response = next((r for r in shuffled_responses if r["text"] == response_r_value), None)
        st.session_state[f"{q_key}_r_value"] = selected_response["r_value"] if selected_response else None
        print(f"Updated response value for {q_key}:", st.session_state[f"{q_key}_r_value"])

    # Review Results button and error message at the bottom together
    if st.button("Review Results"):
        #print("\n=== Review Results button clicked ===")
        st.session_state.validation_attempted = True
        has_unanswered = any(
            not st.session_state.get(f"{q_key}_r_value") for q_key in question_keys
        )
        #print("Has unanswered questions:", has_unanswered)
        
        if has_unanswered:
            #print("Rerunning due to unanswered questions")
            st.rerun()
        else:
            #print("All questions answered, moving to results page")
            st.session_state.page = "results"
            st.rerun()
    
    # Display version number in footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")  # Single horizontal line
    st.markdown(
    f"<span style='font-size:10pt;'>Survey Version: {__version__}</span>", 
    unsafe_allow_html=True
    )
    
    # Show error message right after the button if there are unanswered questions
    if st.session_state.validation_attempted:
        has_unanswered = any(
            not st.session_state.get(f"{q_key}_r_value") for q_key in question_keys
        )
        if has_unanswered:
            print("Displaying error message for unanswered questions")
            st.error("Some questions are unanswered. Please scroll up and complete them before proceeding.")

def display_results_and_chart():
    st.title("Modernity Worldview Survey")
    question_keys = question_manager.get_all_question_keys()

    responses_summary = {}
    individual_scores = []
    n1, n2, n3 = 0, 0, 0

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

        responses_summary[q_key] = (question_text, response_text)

    total = n1 + n2 + n3
    avg_score = [n1 / total * 100, n2 / total * 100, n3 / total * 100] if total > 0 else None

    if individual_scores and avg_score:
        chart = plotter.create_plot(user_scores=individual_scores, avg_score=avg_score)
        plotter.display_plot(chart)
    else:
        st.write("No sufficient data to generate a ternary chart.")

    st.header("Review Your Responses")
    st.markdown("*If you are satisfied with these responses, click the button below to submit your survey.*")
    for q_key, (question_text, response_text) in responses_summary.items():
        st.subheader(question_text)
        st.write(f"▶  {response_text}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Questions"):
            st.session_state.page = "questions"
            st.rerun()
    with col2:
        if st.button("Submit and View Results"):
            # Save to database and fetch updated data
            save_survey_results(st.session_state)
            st.session_state.page = "detailed_results"
            ### st.rerun()


    # Display version number in footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")  # Single horizontal line
    st.markdown(
    f"<span style='font-size:10pt;'>Survey Version: {__version__}</span>", 
    unsafe_allow_html=True
)


def display_detailed_results():
    """Display the detailed results page"""
    if not hasattr(st.session_state, 'final_scores'):
        st.error("No survey data found. Please complete the survey first.")
        if st.button("Return to Survey"):
            st.session_state.page = "questions"
            st.rerun()
        return

    display_results_page(
        st.session_state.final_scores,
        st.session_state.category_responses,
        getattr(st.session_state, 'individual_scores', None)
    )
    
    if st.button("Start New Survey"):
        #print("Start New Survey button clicked")
        st.session_state.clear()
        st.query_params.clear()
        st.switch_page("app.py")  # This forces a complete page reload

def main():
    # Initialise session before anything else
    initialize_session()
    # Determine the current page
    if "page" not in st.session_state:
        st.session_state.page = "questions"  # Default page
    if "error_triggered" not in st.session_state:
        st.session_state.error_triggered = False

    if st.session_state.page == "questions":
        display_questions_and_responses()
    elif st.session_state.page == "results":
        display_results_and_chart()
    elif st.session_state.page == "detailed_results":
        display_detailed_results()

if __name__ == "__main__":
    main()