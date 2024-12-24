import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib.pyplot as plt
import ternary

# Load questions and responses from the JSON file
with open("questions_responses.json", "r") as file:
    data = json.load(file)

question_texts = data["questions"]
response_texts = data["responses"]

# Define scoring data (still kept in Python for simplicity)
responses = {
    "Q1": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q2": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q3": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q4": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q5": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q6": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
}

def calculate_and_debug():
    # Collect all responses
    all_scores = []
    for q, var in question_vars.items():
        response = var.get()
        if not response:
            messagebox.showerror("Error", f"Please answer all questions before submitting.")
            return
        # Fetch the score for the response
        all_scores.append(responses[q][response])

    # Calculate the average score
    avg_score = [
        sum(scores[i] for scores in all_scores) / len(all_scores) for i in range(3)
    ]

    # Create the ternary plot
    figure, tax = ternary.figure(scale=100)  # Single figure
    figure.set_size_inches(10, 8)            # Ensure consistent figure size
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)

    # Custom corner labels
    ax = tax.get_axes()
    ax.text(-0.05, -0.05, "PreModern", fontsize=10, ha="center", va="center", transform=ax.transAxes)  # Bottom-left
    ax.text(1.05, -0.05, "Modern", fontsize=10, ha="center", va="center", transform=ax.transAxes)      # Bottom-right
    ax.text(0.5, 1.05, "PostModern", fontsize=10, ha="center", va="center", transform=ax.transAxes)    # Top-center

    # Plot all individual responses
    tax.scatter(all_scores, marker='o', color='blue', label="Individual Scores")

    # Plot the average score
    tax.scatter([avg_score], marker='o', color='red', label="Aggregated Score")

    # Add debug info text below the triangle
    debug_info = (
        f"Aggregated Score:\n"
        f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}"
    )
    tax.annotate(
        debug_info,
        position=(50, -7.5),  # Position below the triangle
        ha="center",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="red", facecolor="white")
    )

    # Finalize and display the chart
    tax.legend()

    # Explicitly close all previous figures to avoid residual figures
    plt.show()
    plt.close(figure)

    # Save the chart as a PNG file
    figure.savefig("ternary_chart.png")
    print("Ternary chart saved as 'ternary_chart.png'.")


root = tk.Tk()
root.title("Ternary Chart Questionnaire")

question_vars = {}
for question, text in question_texts.items():
    frame = ttk.Frame(root)
    frame.pack(fill="x", padx=10, pady=10)

    question_label = tk.Label(frame, text=text, font=("Arial", 12, "bold"), anchor="w", bg="lightblue", padx=5, pady=5)
    question_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

    var = tk.StringVar(value=None)
    question_vars[question] = var
    for i, (response_key, response_text) in enumerate(response_texts[question].items(), start=1):
        rb = ttk.Radiobutton(frame, text=response_text, variable=var, value=response_key)
        rb.grid(row=i, column=0, sticky="w", padx=20)

submit_button = ttk.Button(root, text="Submit and Plot", command=calculate_and_debug)
submit_button.pack(pady=10)

root.mainloop()
