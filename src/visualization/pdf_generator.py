from fpdf import FPDF
import io

def save_to_pdf(user_scores, avg_score, text_summary):
    """
    Generate a PDF report with user scores, average score, and summary text.
    """
    try:
        # Create a PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Survey Report", ln=True, align="C")

        # Average Score
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt="Average Score:", ln=True)
        pdf.cell(200, 10, txt=f"PreModern: {avg_score[0]:.2f}, Modern: {avg_score[1]:.2f}, PostModern: {avg_score[2]:.2f}", ln=True)

        # Individual Scores
        pdf.ln(10)
        pdf.cell(200, 10, txt="Individual Scores:", ln=True)
        for i, score in enumerate(user_scores, start=1):
            pdf.cell(200, 10, txt=f"Score {i}: PreModern={score[0]:.2f}, Modern={score[1]:.2f}, PostModern={score[2]:.2f}", ln=True)

        # Summary
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=text_summary)

        # Save PDF to a buffer
        buffer = io.BytesIO()
        pdf.output(dest="S").encode("latin1")  # Generate PDF content
        buffer.write(pdf.output(dest="S").encode("latin1"))
        buffer.seek(0)  # Reset the buffer pointer to the beginning

        # Return the buffer contents
        return buffer.getvalue()
    except Exception as e:
        raise RuntimeError(f"Error generating PDF: {e}")
