import ternary

def configure_ternary_chart(tax):
    """
    Apply standard configurations to a ternary plot.

    Parameters:
    - tax: A ternary axis object.

    Returns:
    - The configured ternary axis.
    """
    # Set boundary and gridlines
    tax.boundary(linewidth=1.5)
    tax.gridlines(multiple=10, color="gray", linewidth=0.5)

    # Add axis labels
    tax.left_axis_label("PreModern", fontsize=12, offset=0.16)
    tax.right_axis_label("Modern", fontsize=12, offset=0.16)
    tax.bottom_axis_label("PostModern", fontsize=12, offset=0.04)

    # Return the configured tax object
    return tax
