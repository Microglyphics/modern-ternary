# src/visualization/results_page.py

import streamlit as st
import time
from visualization.report import SurveyReport, save_to_pdf
from version import __version__

def main():
    # Get query parameters
    query_params = st.experimental_get_query_params()

    try:
        # Retrieve and process parameters
        param_start = time.time()
        user_scores = [
            [float(x) for x in score.split(',')]
            for score in query_params.get("user_scores", [])
        ]
        avg_score = [float(x) for x in query_params.get("avg_score", [])]
        
        # Generate the report
        report = SurveyReport()
        chart, text_summary = report.create_full_report(user_scores, avg_score)
        report_end = time.time()
 
        # Display results
        st.title("Survey Results")
        report.plotter.display_plot(chart)
        st.write(text_summary)

        # Add PDF download button
        if st.button("Download Report as PDF"):
            try:
                pdf_start = time.time()
                pdf_buffer = save_to_pdf(user_scores, avg_score, text_summary)
                pdf_end = time.time()
                
                st.download_button(
                    label="Download Report",
                    data=pdf_buffer,
                    file_name="survey_report.pdf",
                    mime="application/pdf"
                )
               
            except Exception as e:
                # logging.error(f"Error generating PDF: {e}")
                st.error("Failed to generate PDF. Please try again.")
    except Exception as e:
        st.error("An error occurred while processing the results.")

if __name__ == "__main__":
    main()