import matplotlib.pyplot as plt
import ternary

# Example data: [PreModern, Modern, PostModern]
data_point = [70, 20, 10]  # Replace with your values

# Initialise figure and axis
figure, tax = ternary.figure(scale=100)

# Set boundary and gridlines
tax.boundary(linewidth=1.5)
tax.gridlines(multiple=10, color="gray", linewidth=0.5)

# Plot the point
tax.scatter([data_point], marker='o', color='red', label="Example Point", vmin=None, vmax=None)
tax.ticks(axis='lbr', multiple=10)

# Labels
tax.left_axis_label("PreModern", fontsize=10, offset=0.16)
tax.right_axis_label("Modern", fontsize=10, offset=0.16)
tax.bottom_axis_label("PostModern", fontsize=10, offset=0.06)

# Display
tax.legend()
plt.show()
