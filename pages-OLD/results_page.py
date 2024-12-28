import streamlit as st
from src.visualization.report import SurveyReport
from visualization.report import save_to_pdf
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import logging
# from fpdf import FPDF
# import io

# Configure logging
logging.basicConfig(
    filename='debug.log',  # Log file name
    level=logging.DEBUG,   # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log to console as well
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def main():
    # Retrieve query parameters
    parsed_params = st.query_params  # Directly use st.query_params
    logging.debug(f"Parsed Query Parameters via st.query_params: {parsed_params}")
    st.write("Parsed Query Parameters:", parsed_params)

    # Parse user_scores
    try:
        user_scores_raw = st.query_params.get("user_scores", "")
        logging.debug(f"Raw user_scores_raw (Before Conversion): {user_scores_raw}")

        # Ensure it's processed as a string
        if user_scores_raw:
            user_scores_raw = str(user_scores_raw)
            logging.debug(f"Raw user_scores_raw (After Conversion): {user_scores_raw}")

            # Split into floats
            user_scores_list = [float(x.strip()) for x in user_scores_raw.split(",") if x.strip()]
            logging.debug(f"Parsed user_scores_list (Flat): {user_scores_list}")

            # Group into ternary points
            user_scores = [user_scores_list[i:i + 3] for i in range(0, len(user_scores_list), 3)]
            logging.debug(f"Parsed user_scores (Chunked): {user_scores}")
        else:
            user_scores = []
            logging.debug("user_scores_raw is empty or invalid.")
    except Exception as e:
        logging.error(f"Error parsing user_scores: {e}")
        user_scores = []

    # Parse avg_score
    try:
        avg_score_str = st.query_params.get("avg_score", "")
        logging.debug(f"Raw avg_score_str (Before Conversion): {avg_score_str}")

        # Ensure it's processed as a string
        if avg_score_str:
            avg_score_str = str(avg_score_str)
            logging.debug(f"Raw avg_score_str (After Conversion): {avg_score_str}")

            # Split into floats
            avg_score = [float(x.strip()) for x in avg_score_str.split(",") if x.strip()]
            logging.debug(f"Parsed avg_score: {avg_score}")
        else:
            avg_score = []
            logging.debug("avg_score_str is empty or invalid.")
    except Exception as e:
        logging.error(f"Error parsing avg_score: {e}")
        avg_score = []

    # Validate avg_score
    logging.debug(f"Final avg_score (Post-Validation): {avg_score}")
    st.write("Final avg_score (Post-Validation):", avg_score)
    if len(avg_score) != 3:
        st.error("Invalid average score format. Please check the query parameters.")
        return

    # Debug final values
    logging.debug(f"Final user_scores (Post-Processing): {user_scores}")
    st.write("Final user_scores (Post-Processing):", user_scores)
    logging.debug(f"Final avg_score (Post-Processing): {avg_score}")
    st.write("Final avg_score (Post-Processing):", avg_score)

    # Generate the report
    report = SurveyReport()
    try:
        chart, text_summary = report.create_full_report(user_scores, avg_score)
        st.title("Survey Results")
        report.plotter.display_plot(chart)
        st.write(text_summary)

        # Add PDF download button
        if st.button("Download Report as PDF"):
            try:
                pdf_buffer = save_to_pdf(
                    user_scores,
                    avg_score,
                    "Explanation of PreModern, Modern, and PostModern characteristics..."
                )
                st.download_button(
                    label="Download Report",
                    data=pdf_buffer,
                    file_name="survey_report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
    except Exception as e:
        st.error(f"Error generating report: {e}")

if __name__ == "__main__":
    main()
