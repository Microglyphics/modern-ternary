import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import ternary

# Scoring data for debugging
responses = {
    "Q1": {
        "R1": [100, 0, 0],  # PreModern
        "R2": [0, 100, 0],  # Modern
        "R3": [0, 0, 100],  # PostModern
        "R4": [50, 50, 0],  # Mixed: PreModern and Modern
        "R5": [0, 50, 50],  # Mixed: Modern and PostModern
    }
}

# Question text
question_texts = {
    "Q1": "1. What is the source of truth?",
}

# Response text
response_texts = {
    "Q1": [
        "R1: Truth is given by divine or spiritual authority.",
        "R2: Truth is discovered through empirical evidence.",
        "R3: Truth is shaped by cultural or personal perspectives.",
        "R4: Truth is primarily divine but interpreted through reason.",
        "R5: Truth is mostly objective but influenced by culture.",
    ],
}

# Function to calculate, display the score, and plot the chart
def calculate_and_debug():
    # Get the selected response
    selected_response = question_var.get()
    if not selected_response:
        messagebox.showerror("Error", "Please select a response.")
        return

    # Fetch the score for the selected response
    score = responses["Q1"][selected_response]
    response_message = (
        f"Selected Response: {selected_response}\n"
        f"Score: {score}\n"
        f"PreModern: {score[0]}, Modern: {score[1]}, PostModern: {score[2]}"
    )

    # Create the ternary plot with larger size
    figure, tax = ternary.figure(scale=100)
    figure.set_size_inches(10, 8)  # Resize the figure
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)

    # Custom corner labels using ax.text()
    ax = tax.get_axes()
    ax.text(-0.05, -0.05, "PostModern", fontsize=10, ha="center", va="center", transform=ax.transAxes)  # Bottom-left
    ax.text(1.05, -0.05, "PreModern", fontsize=10, ha="center", va="center", transform=ax.transAxes)      # Bottom-right
    ax.text(0.5, 1.05, "Modern", fontsize=10, ha="center", va="center", transform=ax.transAxes)    # Top-center

    # Plot the selected score
    tax.scatter([score], marker='o', color='red', label="Selected Score")

    # Add debug info in the reserved area
    ax.text(
        0, 1.05,  # Normalized figure coordinates
        response_message,
        fontsize=10,
        color="black",
        bbox=dict(facecolor="white", edgecolor="red", boxstyle="round,pad=0.5"),
        transform=ax.transAxes,  # Use normalized coordinates
        ha="left",
    )

    # Finalize and display the chart
    tax.legend()
    plt.show()

# Create the GUI
root = tk.Tk()
root.title("Debugging Questionnaire: Question 1")

frame = ttk.Frame(root)
frame.pack(fill="x", padx=10, pady=10)

# Add question label
question_label = tk.Label(frame, text=question_texts["Q1"], font=("Arial", 12, "bold"), anchor="w", bg="lightblue")
question_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

# Add response options
question_var = tk.StringVar(value=None)
for i, (response_text, response_key) in enumerate(zip(response_texts["Q1"], responses["Q1"].keys()), start=1):
    rb = ttk.Radiobutton(frame, text=response_text, variable=question_var, value=response_key)
    rb.grid(row=i, column=0, sticky="w", padx=20)

# Add a submit button
submit_button = ttk.Button(root, text="Submit and Debug", command=calculate_and_debug)
submit_button.pack(pady=20)

root.mainloop()
