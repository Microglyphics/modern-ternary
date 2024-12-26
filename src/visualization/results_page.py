# src/visualization/results_page.py

import streamlit as st
import logging
import time
from visualization.report import SurveyReport, save_to_pdf

# Configure logging
logging.basicConfig(
    filename='debug.log',  # Log file name
    level=logging.DEBUG,    # Adjust to DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    start_time = time.time()
    logging.info("Starting results page...")

    # Get query parameters
    query_params = st.experimental_get_query_params()
    logging.info(f"Query parameters retrieved: {query_params}")

    try:
        # Retrieve and process parameters
        param_start = time.time()
        user_scores = [
            [float(x) for x in score.split(',')]
            for score in query_params.get("user_scores", [])
        ]
        avg_score = [float(x) for x in query_params.get("avg_score", [])]
        param_end = time.time()
        logging.info(f"Parameter processing completed in {param_end - param_start:.2f} seconds.")

        # Generate the report
        report_start = time.time()
        report = SurveyReport()
        chart, text_summary = report.create_full_report(user_scores, avg_score)
        report_end = time.time()
        logging.info(f"Report generation completed in {report_end - report_start:.2f} seconds.")

        # Display results
        st.title("Survey Results")
        report.plotter.display_plot(chart)
        st.write(text_summary)
        logging.info("Survey results displayed.")

        # Add PDF download button
        if st.button("Download Report as PDF"):
            try:
                pdf_start = time.time()
                pdf_buffer = save_to_pdf(user_scores, avg_score, text_summary)
                pdf_end = time.time()
                logging.info(f"PDF generation completed in {pdf_end - pdf_start:.2f} seconds.")

                st.download_button(
                    label="Download Report",
                    data=pdf_buffer,
                    file_name="survey_report.pdf",
                    mime="application/pdf"
                )
                logging.info("PDF download button rendered successfully.")
            except Exception as e:
                logging.error(f"Error generating PDF: {e}")
                st.error("Failed to generate PDF. Please try again.")
    except Exception as e:
        logging.error(f"Error processing results page: {e}")
        st.error("An error occurred while processing the results.")

    # Debugging stuff
    end_time = time.time()
    st.write(f"Total page load time: {end_time - start_time:.2f} seconds.")
    logging.info(f"Total page load time: {end_time - start_time:.2f} seconds.")
    logging.info("Results page processing complete.")

if __name__ == "__main__":
    main()