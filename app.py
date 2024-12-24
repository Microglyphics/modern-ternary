import streamlit as st
import random
import matplotlib.pyplot as plt
import ternary
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

# Collect user responses
user_responses = {}
for q_key, question in questions.items():
    st.subheader(question)
    
    # Persistent instruction (dual-purpose message)
    placeholder_message = "Select an option from the list below to proceed."

    # Combine the placeholder with actual responses
    options = [placeholder_message] + responses[q_key]
    random.shuffle(responses[q_key])  # Randomise only the actual responses
    
    # Render the radio button with dynamic feedback
    selected_option = st.radio(
        "", options, index=0, key=q_key
    )

    # Customise the warning text (embedded under the question)
    if selected_option == placeholder_message:
        st.markdown(
            f"<div style='color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; "
            f"padding: 10px; border-radius: 5px;'>"
            f"Please select an option for <b>{question}</b>.</div>",
            unsafe_allow_html=True,
        )
    
    # Save only the valid response
    user_responses[q_key] = None if selected_option == placeholder_message else selected_option

# Submit button
if st.button("Submit"):
    st.write("Thank you for your responses!")
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
