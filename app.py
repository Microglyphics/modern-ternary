import streamlit as st
import random
import matplotlib.pyplot as plt
import ternary # This is the chart object
import sqlite3

# Questions and responses
questions = {
    "Q1": "1. What is the source of truth?",
    "Q2": "2. What is the best way to understand the world?",
    "Q3": "3. How is knowledge best gained?",
    "Q4": "4. What is your view of the world?",
    "Q5": "5. How should societal values be oriented?",
    "Q6": "6. How is identity defined?",
}

responses = {
    "Q1": [
        "Truth is given by divine or spiritual authority.",
        "Truth is discovered through empirical evidence.",
        "Truth is shaped by cultural or personal perspectives.",
        "Truth is primarily divine but interpreted through reason.",
        "Truth is mostly objective but influenced by culture.",
    ],
    "Q2": [
        "Understand the world through sacred traditions.",
        "Understand the world by uncovering universal principles.",
        "Critique and question established assumptions.",
        "Sacred stories reveal truths but must align with reason.",
        "Universal principles exist but are shaped by culture.",
    ],
    "Q3": [
        "Knowledge is gained through spiritual intuition.",
        "Knowledge is gained through logical reasoning.",
        "Knowledge is gained by questioning existing ideas.",
        "Mystical insights must be balanced with reasoning.",
        "Logical reasoning is essential but subjective.",
    ],
    "Q4": [
        "The world is governed by a divine cosmic order.",
        "The world progresses through scientific advancements.",
        "The world is a critique of traditional systems.",
        "Cosmic order exists, but progress plays a role.",
        "Progress must be critically examined through irony.",
    ],
    "Q5": [
        "Societal values follow established traditions.",
        "Values are guided by objective, neutral standards.",
        "Values adapt to subjective or situational contexts.",
        "Respect traditions but balance with objectivity.",
        "Objective standards must consider subjective contexts.",
    ],
    "Q6": [
        "Identity is defined by one’s role in a community.",
        "Identity is discovered through personal authenticity.",
        "Identity is fluid and changes with contexts.",
        "Identity is collective but allows personal expression.",
        "Identity is personal but adapts to fluid contexts.",
    ],
}

# Database setup
def init_db():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            response TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def save_response(question, response):
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO survey_responses (question, response) VALUES (?, ?)", (question, response)
    )
    conn.commit()
    conn.close()

# App title
st.title("Ternary Chart Questionnaire")

# Initialize database
init_db()

# Flag for whether all questions are answered
all_questions_answered = True

# Check if 'randomised_responses' is already stored in session_state
def get_randomised_options(q_key, options):
    if "randomised_responses" not in st.session_state:
        st.session_state.randomised_responses = {}
    if q_key not in st.session_state.randomised_responses:
        st.session_state.randomised_responses[q_key] = random.sample(options, len(options))
    return st.session_state.randomised_responses[q_key]

# Add a warning for unanswered questions
def show_warning():
    st.warning("⚠️ Please select an option for this question.")

# Collect user responses with a top empty choice
user_responses = {}
for q_key, question in questions.items():
    # Display the question
    st.subheader(question)

    # Add placeholder for warning message (dynamically inserted)
    warning_placeholder = st.empty()

    # Add empty top choice and randomised options
    options = ["Select an option from the list below to proceed."] + get_randomised_options(q_key, responses[q_key])

    # Capture user response
    user_choice = st.radio("", options, key=q_key)

    # Display warning if the first option (empty choice) is selected
    if user_choice == "Select an option from the list below to proceed.":
        warning_placeholder.warning("⚠️ Please select an option.")
    else:
        warning_placeholder.empty()  # Clear the warning if a valid option is selected

    # Save the response
    if user_choice != "Select an option from the list below to proceed.":
        user_responses[q_key] = user_choice

# Flag to check if all questions are answered
all_questions_answered = all(
    user_responses.get(q_key) and user_responses[q_key] != "Select an option from the list below to proceed."
    for q_key in questions
)

# Disable the Submit button if not all questions are answered
if not all_questions_answered:
    st.warning("⚠️ Please answer all questions before submitting.")

# Submit button logic
if st.button("Submit", disabled=not all_questions_answered):
    st.write("Thank you for your responses!")

    # Save responses or process them here
    st.write("Your responses are:", user_responses)

    # Save responses to database
    for q, r in user_responses.items():
        save_response(q, r)

    # Simulate aggregated results for ternary chart (replace with real logic)
    individual_scores = [[random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)] for _ in range(6)]
    avg_score = [
        sum(x) / len(individual_scores) for x in zip(*individual_scores)
    ]

    # Generate ternary chart
    figure, tax = ternary.figure(scale=100)
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)
    tax.scatter(individual_scores, marker='o', color='blue', label="Individual Scores")
    tax.scatter([avg_score], marker='o', color='red', label="Aggregated Score")
    tax.legend()
    tax.annotate(
        f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}",
        position=(50, -10),
        ha="center",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="red", facecolor="white"),
    )
    st.pyplot(figure)

    # Display explanation
    st.write("Based on your responses, here’s your position on the ternary chart:")
    st.write("Explanation of PreModern, Modern, and PostModern characteristics...")

# Footer
st.write("Your responses are saved anonymously and will be used for research purposes.")
