import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import ternary

# Scoring data from file
responses = {
    "Q1": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q2": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q3": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q4": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q5": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
    "Q6": {"R1": [100, 0, 0], "R2": [0, 100, 0], "R3": [0, 0, 100], "R4": [50, 50, 0], "R5": [0, 50, 50]},
}

# Function to calculate and plot the aggregate score
def calculate_and_plot():
    total = [0, 0, 0]
    for q, var in question_vars.items():
        response = var.get()
        if response:
            scores = responses[q][response]
            total = [t + s for t, s in zip(total, scores)]
    # Calculate average
    avg = [t / len(question_vars) for t in total]

    # Plot on ternary chart
    figure, tax = ternary.figure(scale=100)
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)
    tax.scatter([avg], marker='o', color='red', label="Aggregated Score")
    tax.left_axis_label("PreModern", fontsize=10)
    tax.right_axis_label("Modern", fontsize=10)
    tax.bottom_axis_label("PostModern", fontsize=10)
    tax.legend()
    plt.show()

# Create the GUI
root = tk.Tk()
root.title("Ternary Chart Questionnaire")

question_vars = {}
for i, question in enumerate(responses.keys(), 1):
    frame = ttk.Frame(root)
    frame.pack(fill="x", padx=5, pady=5)

    label = ttk.Label(frame, text=f"{question}:", width=20)
    label.pack(side="left")

    var = tk.StringVar(value=None)
    question_vars[question] = var
    for response in responses[question].keys():
        rb = ttk.Radiobutton(frame, text=response, variable=var, value=response)
        rb.pack(side="left")

# Add a submit button
submit_button = ttk.Button(root, text="Submit and Plot", command=calculate_and_plot)
submit_button.pack(pady=10)

root.mainloop()
