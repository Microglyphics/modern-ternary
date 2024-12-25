import streamlit as st
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from questions.question_manager import QuestionManager
from visualization.ternary_plotter import TernaryPlotter
from data.data_handler import DataHandler

def main():
    st.title("Worldview Survey")
    
    # Initialize components
    question_manager = QuestionManager()
    plotter = TernaryPlotter()
    data_handler = DataHandler()
    
    # Track responses
    user_responses = {}
    user_scores = []
    all_questions_answered = True
    
    # Display questions
    for q_key in question_manager.get_all_question_keys():
        st.subheader(question_manager.get_question_text(q_key))
        
        # Get randomized options
        options = question_manager.get_randomized_options(q_key, st.session_state)
        option_texts = [opt["text"] for opt in options]
        option_texts.insert(0, "Select an option from the list below to proceed.")
        
        # Display radio button
        user_choice = st.radio("", option_texts, key=f"radio_{q_key}")
        
        if user_choice == "Select an option from the list below to proceed.":
            st.warning(f"⚠️ Please select an option for question {q_key}.")
            all_questions_answered = False
        else:
            for opt in options:
                if opt["text"] == user_choice:
                    user_scores.append(opt["scores"])
                    user_responses[q_key] = user_choice
                    break
    
    # Submit button with custom styling
    button_style = """
        <style>
        div.stButton > button:first-child {
            background-color: rgb(45, 201, 55);
            color: white;
        }
        div.stButton > button:hover {
            background-color: rgb(40, 180, 50);
            color: white;
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    if st.button("Submit", key="submit_button", use_container_width=True):
        if all_questions_answered:
            if question_manager.validate_responses(user_responses, user_scores):
                # Calculate average score
                avg_score = data_handler.calculate_average_score(user_scores)
                
                # Save response
                data_handler.save_response(user_responses, user_scores)
                
                # Create and display plot
                fig = plotter.create_plot(user_scores, avg_score)
                plotter.display_plot(fig)
                
                # Display explanation
                st.write("Based on your responses, here's your position on the ternary chart:")
                st.write("Explanation of PreModern, Modern, and PostModern characteristics...")
            else:
                st.error("Invalid response data. Please try again.")
        else:
            st.error("⚠️ Please answer all questions before submitting!")
    
    # Footer
    st.write("Your responses are saved anonymously and will be used for research purposes.")

if __name__ == "__main__":
    main()
