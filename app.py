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

# Add custom CSS style for the button
st.markdown("""
    <style>
        .stButton > button {
            background-color: #4CAF50;  /* Green color */
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Submit button logic
if st.button("Submit", key="submit_button"):
    if all_questions_answered:
        avg_score = validate_and_process()

        # Create matplotlib figure first (only once)
        figure, ax = plt.subplots()

        # Create the ternary axes (only once)
        scale = 100
        tax = ternary.TernaryAxesSubplot(ax=ax, scale=scale)

        # Add boundary and gridlines
        tax.boundary(linewidth=1.5)
        tax.gridlines(multiple=10, color="gray", linewidth=0.5)

        # Generate tick positions in percentage format (0 to 100)
        ticks = range(0, 101, 10)  # This creates [0, 10, 20, ..., 100]

        # Add ticks with labels
        tax.ticks(ticks=ticks, 
                axis='lbr',  # left, bottom, right
                linewidth=1, 
                multiple=10,
                offset=0.02)

        tax.clear_matplotlib_ticks()

        # Add corner labels
        tax.left_corner_label("PostModern", fontsize=12, offset=0.15)
        tax.top_corner_label("Modern", fontsize=12, offset=0.15)
        tax.right_corner_label("PreModern", fontsize=12, offset=0.15)

        # Add interior triangle connecting 50% points
        line_kwargs = {
            'color': 'blue',
            'linestyle': '-',
            'linewidth': 2.0,
            'alpha': 1.0,
            'zorder': 10
        }

        # Convert percentages to proportions (50% = 0.5)
        point1 = (0.5, 0.5, 0)     # Bottom point (PreMod=50, Mod=50, Post=0)
        point2 = (0.5, 0, 0.5)     # Right point  (PreMod=50, Mod=0, Post=50)
        point3 = (0, 0.5, 0.5)     # Left point   (PreMod=0, Mod=50, Post=50)

        # Draw the interior triangle
        tax.line(point1, point2, **line_kwargs)
        tax.line(point2, point3, **line_kwargs)
        tax.line(point3, point1, **line_kwargs)

        # Plot the data points
        if user_scores:
            tax.scatter(user_scores, marker='o', color='blue', label="Individual Scores")
        
        # Highlight the aggregated score
        tax.scatter([avg_score], marker='o', color='red', label="Aggregated Score")

        # Add legend
        tax.legend()

        # Show the plot
        st.pyplot(figure)

        # Explanation of the results
        st.write("Based on your responses, here's your position on the ternary chart:")
        st.write("Explanation of PreModern, Modern, and PostModern characteristics...")
    else:
        st.error("⚠️ Please answer all questions before submitting!")

# Footer
st.write("Your responses are saved anonymously and will be used for research purposes.")
