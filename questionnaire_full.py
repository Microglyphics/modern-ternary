# Import dependencies
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import ternary

# Scoring data with textual responses
responses = {
    "Q1": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
    "Q2": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
    "Q3": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
    "Q4": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
    "Q5": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
    "Q6": {
        "R1": [100, 0, 0],
        "R2": [0, 100, 0],
        "R3": [0, 0, 100],
        "R4": [50, 50, 0],
        "R5": [0, 50, 50],
    },
}

# Textual questions and responses for readability
question_texts = {
    "Q1": "1. What is the source of truth?",
    "Q2": "2. What is the best way to understand the world?",
    "Q3": "3. How is knowledge best gained?",
    "Q4": "4. What is your view of the world?",
    "Q5": "5. How should societal values be oriented?",
    "Q6": "6. How is identity defined?",
}

response_texts = {
    "Q1": [
        "R1: Truth is given by divine or spiritual authority.",
        "R2: Truth is discovered through empirical evidence.",
        "R3: Truth is shaped by cultural or personal perspectives.",
        "R4: Truth is primarily divine but interpreted through reason.",
        "R5: Truth is mostly objective but influenced by culture.",
    ],
    "Q2": [
        "R1: Understand the world through sacred traditions.",
        "R2: Understand the world by uncovering universal principles.",
        "R3: Critique and question established assumptions.",
        "R4: Sacred stories reveal truths but must align with reason.",
        "R5: Universal principles exist but are shaped by culture.",
    ],
    "Q3": [
        "R1: Knowledge is gained through spiritual intuition.",
        "R2: Knowledge is gained through logical reasoning.",
        "R3: Knowledge is gained by questioning existing ideas.",
        "R4: Mystical insights must be balanced with reasoning.",
        "R5: Logical reasoning is essential but subjective.",
    ],
    "Q4": [
        "R1: The world is governed by a divine cosmic order.",
        "R2: The world progresses through scientific advancements.",
        "R3: The world is a critique of traditional systems.",
        "R4: Cosmic order exists, but progress plays a role.",
        "R5: Progress must be critically examined through irony.",
    ],
    "Q5": [
        "R1: Societal values follow established traditions.",
        "R2: Values are guided by objective, neutral standards.",
        "R3: Values adapt to subjective or situational contexts.",
        "R4: Respect traditions but balance with objectivity.",
        "R5: Objective standards must consider subjective contexts.",
    ],
    "Q6": [
        "R1: Identity is defined by one’s role in a community.",
        "R2: Identity is discovered through personal authenticity.",
        "R3: Identity is fluid and changes with contexts.",
        "R4: Identity is collective but allows personal expression.",
        "R5: Identity is personal but adapts to fluid contexts.",
    ],
}


def calculate_and_debug():
    # Collect all responses
    all_scores = []
    for q, var in question_vars.items():
        response = var.get()
        if not response:
            messagebox.showerror("Error", "Please answer all questions before submitting.")
            return
        all_scores.append(responses[q][response])

    # Calculate aggregate score
    total = [0, 0, 0]
    for scores in all_scores:
        total = [t + s for t, s in zip(total, scores)]
    avg = [t / len(all_scores) for t in total]

    # Debug info
    debug_info = f"Aggregated Score:\nPreModern: {avg[0]:.2f}, Modern: {avg[1]:.2f}, PostModern: {avg[2]:.2f}"

    # Create ternary plot
    figure, tax = ternary.figure(scale=100)
    figure.set_size_inches(10, 8)
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)

    # Custom corner labels
    ax = tax.get_axes()
    ax.text(-0.05, -0.05, "PreModern", fontsize=10, ha="center", transform=ax.transAxes)
    ax.text(1.05, -0.05, "Modern", fontsize=10, ha="center", transform=ax.transAxes)
    ax.text(0.5, 1.05, "PostModern", fontsize=10, ha="center", transform=ax.transAxes)

    # Plot individual scores and average
    tax.scatter(all_scores, marker='o', color='blue', label="Individual Scores")
    tax.scatter([avg], marker='o', color='red', label="Aggregated Score")

    # Add debug info
    tax.annotate(debug_info, position=(50, -8), ha="center", fontsize=10, bbox=dict(boxstyle="round,pad=0.5", edgecolor="red", facecolor="white"))

    # Finalize plot
    tax.legend()
    plt.show()


# Create the GUI
root = tk.Tk()
root.title("Ternary Chart Questionnaire")

question_vars = {}
for question, text in question_texts.items():
    frame = ttk.Frame(root)
    frame.pack(fill="x", padx=10, pady=10)

    question_label = tk.Label(frame, text=text, font=("Arial", 12, "bold"), bg="lightblue")
    question_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

    var = tk.StringVar(value=None)
    question_vars[question] = var
    for i, (response_text, response_key) in enumerate(zip(response_texts[question], responses[question].keys()), start=1):
        rb = ttk.Radiobutton(frame, text=response_text, variable=var, value=response_key)
        rb.grid(row=i, column=0, sticky="w", padx=20)

    separator = ttk.Separator(frame, orient="horizontal")
    separator.grid(row=i + 1, column=0, sticky="ew", pady=(10, 5))

submit_button = ttk.Button(root, text="Submit and Plot", command=calculate_and_debug)
submit_button.pack(pady=20)

root.mainloop()
