import streamlit as st
import random
import matplotlib.pyplot as plt
import ternary  # This is the chart object
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

# Track responses
user_responses = {}
user_scores = []  # To collect numerical scores for plotting
all_questions_answered = True

# Loop through questions and collect responses
for q_key, question in questions.items():
    st.subheader(question)

    # Add placeholder for warning message
    warning_placeholder = st.empty()

    # Include an empty placeholder option with randomised options
    options = ["Select an option from the list below to proceed."] + responses[q_key]

    # Show the radio button with text options
    user_choice = st.radio("", options, key=q_key)

    # Check the selected response
    if user_choice == "Select an option from the list below to proceed.":
        warning_placeholder.warning("⚠️ Please select an option.")
        all_questions_answered = False
    else:
        warning_placeholder.empty()  # Clear warning
        user_responses[q_key] = user_choice
        user_scores.append([random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)])  # Simulated scores

# Submit button handler
def validate_and_process():
    if not all_questions_answered:
        st.error("⚠️ Please answer all questions before submitting!")
        st.stop()

    # Debugging: Print user responses and scores
    st.write("Debug Info:")
    st.write("User Responses:", user_responses)
    st.write("User Scores:", user_scores)

    # Calculate the average score
    avg_score = [
        sum(x) / len(user_scores) for x in zip(*user_scores)
    ]
    return avg_score

# Submit button
if st.button("Submit", key="submit_button"):
    avg_score = validate_and_process()

    # Generate the ternary chart
    figure, tax = ternary.figure(scale=100)
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)
    tax.scatter(user_scores, marker='o', color='blue', label="Individual Scores")
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

    # Explanation of the results
    st.write("Based on your responses, here’s your position on the ternary chart:")
    st.write("Explanation of PreModern, Modern, and PostModern characteristics...")

# Footer
st.write("Your responses are saved anonymously and will be used for research purposes.")
