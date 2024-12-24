import streamlit as st
import random
import matplotlib.pyplot as plt
import ternary # this is python-ternary
import json

# Load questions and responses from external JSON file
with open('questions_responses.json', 'r') as file:
    data = json.load(file)

# App title
st.title("Modernity Placement Questionnaire")

# Extract questions and responses
questions = {key: value["text"] for key, value in data["questions"].items()}
responses = {key: value["responses"] for key, value in data["questions"].items()}

# Track responses
user_responses = {}
user_scores = []  # To collect numerical scores for plotting
all_questions_answered = True

# Function to randomise responses once and store in session state
def get_randomised_options(q_key, options):
    if "randomised_responses" not in st.session_state:
        st.session_state.randomised_responses = {}
    if q_key not in st.session_state.randomised_responses:
        st.session_state.randomised_responses[q_key] = random.sample(options, len(options))
    return st.session_state.randomised_responses[q_key]

for q_key, question in questions.items():
    st.subheader(question)

    # Get randomised options from session state
    options = get_randomised_options(q_key, responses[q_key])
    option_texts = [opt["text"] for opt in options]
    option_texts.insert(0, "Select an option from the list below to proceed.")

    # Display the radio button for the question
    user_choice = st.radio("", option_texts, key=f"radio_{q_key}")

    # Check if the user selected a valid option
    if user_choice == "Select an option from the list below to proceed.":
        st.warning(f"⚠️ Please select an option for question {q_key}.")
        all_questions_answered = False
    else:
        # Find the selected option and append its score
        for opt in options:
            if opt["text"] == user_choice:
                user_scores.append(opt["scores"])
                break
        user_responses[q_key] = user_choice

# Submit button handler
def validate_and_process():
    if len(user_scores) != len(questions):
        st.error("⚠️ Please answer all questions before submitting!")
        st.stop()

    # Ensure all scores are valid triples
    if not all(isinstance(score, list) and len(score) == 3 and all(isinstance(val, (int, float)) for val in score) for score in user_scores):
        st.error("Invalid data detected. Please ensure all responses are valid.")
        st.stop()

    # Calculate the average score
    avg_score = [
        sum(x) / len(user_scores) for x in zip(*user_scores)
    ]
    return avg_score

# The rest of your imports and setup code remains the same...

if st.button("Submit", key="submit_button"):
    if all_questions_answered:
        avg_score = validate_and_process()

        # Generate the ternary chart
        figure, tax = ternary.figure(scale=100)
        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Add axis labels for the ternary chart
        # Create matplotlib figure first
        figure, ax = plt.subplots()

        # Create the ternary axes
        scale = 100
        tax = ternary.TernaryAxesSubplot(ax=ax, scale=scale)

        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Update axis labels with correct positions
        # PostModern on lower-left
        tax.left_corner_label("PostModern", fontsize=12, offset=0.15)

        # Modern at top-center
        tax.top_corner_label("Modern", fontsize=12, offset=0.15)

        # PreModern on lower-right
        tax.right_corner_label("PreModern", fontsize=12, offset=0.15)

        # Plot individual scores
        if user_scores:
            tax.scatter(user_scores, marker='o', color='blue', label="Individual Scores")
        
        # Highlight the aggregated score
        tax.scatter([avg_score], marker='o', color='red', label="Aggregated Score")

        # Add a legend and an annotation for the aggregated score
        tax.legend()
        tax.annotate(
            f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}",
            position=(50, -7.5),
            ha="center",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", edgecolor="red", facecolor="white"),
        )

        # Render the chart
        st.pyplot(figure)

        # Explanation of the results
        st.write("Based on your responses, here's your position on the ternary chart:")
        st.write("Explanation of PreModern, Modern, and PostModern characteristics...")
    else:
        st.error("⚠️ Please answer all questions before submitting!")

# Footer
st.write("Your responses are saved anonymously and will be used for research purposes.")
