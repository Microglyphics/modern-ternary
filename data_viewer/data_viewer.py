import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import sys
import os
import sqlite3
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from data.sqlite_utils import SQLiteManager
from src.data.db_manager import append_record, DB_PATH

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SurveyDataViewer:
    def __init__(self, db_path: str = 'questionnaire_responses.db'):
        """Initialize viewer with database connection"""
        logger.debug(f"Initializing SurveyDataViewer with database path: {db_path}")
        self.db_path = db_path
        self.db = SQLiteManager(db_path)
        self.load_data()

    def load_data(self):
        """Load response data from database"""
        try:
            logger.debug("Attempting to load response data")
            with sqlite3.connect(self.db_path) as conn:
                self.responses_df = pd.read_sql_query("""
                    SELECT 
                        timestamp,
                        q1_response, q2_response, q3_response, 
                        q4_response, q5_response, q6_response,
                        n1, n2, n3, plot_x, plot_y,
                        session_id, source, version, browser, region
                    FROM survey_results 
                    ORDER BY timestamp DESC
                """, conn)
            
            if not self.responses_df.empty:
                logger.debug(f"Loaded {len(self.responses_df)} records")
                # Convert timestamp to datetime
                self.responses_df['timestamp'] = pd.to_datetime(self.responses_df['timestamp'])
            else:
                logger.warning("No data found in survey_results table")
                self.responses_df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading responses: {e}", exc_info=True)
            st.error(f"Error loading data: {str(e)}")
            self.responses_df = pd.DataFrame()

    def show_response_analysis(self):
        """Show response analysis"""
        st.header("Response Analysis")

        if self.responses_df.empty:
            st.warning("No response data available yet.")
            return

        # Basic stats
        st.subheader("Response Summary")
        total_responses = len(self.responses_df)
        st.write(f"Total Responses: {total_responses}")

        # Version distribution
        if 'version' in self.responses_df.columns:
            st.subheader("Version Distribution")
            version_counts = self.responses_df['version'].value_counts()
            st.bar_chart(version_counts)

        # Source distribution
        if 'source' in self.responses_df.columns:
            st.subheader("Source Distribution")
            source_counts = self.responses_df['source'].value_counts()
            st.bar_chart(source_counts)

        # Data table with filters
        st.subheader("Response Details")
        with st.expander("Filter Options"):
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                if 'version' in self.responses_df.columns:
                    selected_version = st.multiselect(
                        "Filter by Version",
                        options=self.responses_df['version'].unique()
                    )
            with col2:
                if 'source' in self.responses_df.columns:
                    selected_source = st.multiselect(
                        "Filter by Source",
                        options=self.responses_df['source'].unique()
                    )

        # Apply filters
        filtered_df = self.responses_df
        if 'version' in self.responses_df.columns and selected_version:
            filtered_df = filtered_df[filtered_df['version'].isin(selected_version)]
        if 'source' in self.responses_df.columns and selected_source:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_source)]

        # Display filtered dataframe
        st.dataframe(filtered_df, height=500)

        # Show responses over time
        st.subheader("Responses Over Time")
        responses_by_day = self.responses_df.resample('D', on='timestamp').size()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        responses_by_day.plot(ax=ax)
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Responses')
        ax.set_title('Daily Response Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    def show_score_distribution(self):
        """Show score distribution analysis"""
        st.header("Score Distribution Analysis")

        if self.responses_df.empty:
            st.warning("No response data available yet.")
            return

        # Add filters
        with st.expander("Filter Options"):
            col1, col2 = st.columns(2)
            with col1:
                if 'version' in self.responses_df.columns:
                    selected_version = st.multiselect(
                        "Filter by Version",
                        options=self.responses_df['version'].unique()
                    )
            with col2:
                if 'source' in self.responses_df.columns:
                    selected_source = st.multiselect(
                        "Filter by Source",
                        options=self.responses_df['source'].unique()
                    )

        # Apply filters
        filtered_df = self.responses_df
        if 'version' in self.responses_df.columns and selected_version:
            filtered_df = filtered_df[filtered_df['version'].isin(selected_version)]
        if 'source' in self.responses_df.columns and selected_source:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_source)]

        # Score distribution
        st.subheader("Distribution of Scores")
        
        # Box plot
        fig, ax = plt.subplots(figsize=(10, 6))
        filtered_df[['n1', 'n2', 'n3']].boxplot(ax=ax)
        ax.set_title('Score Distribution by Category')
        ax.set_ylabel('Score')
        ax.set_xticklabels(['PreModern', 'Modern', 'PostModern'])
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Violin plot for more detailed distribution view
        st.subheader("Detailed Score Distribution")
        fig, ax = plt.subplots(figsize=(10, 6))
        score_data = pd.melt(filtered_df[['n1', 'n2', 'n3']], 
                            var_name='Category', 
                            value_name='Score')
        sns.violinplot(data=score_data, x='Category', y='Score', ax=ax)
        ax.set_xticklabels(['PreModern', 'Modern', 'PostModern'])
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Summary statistics
        st.subheader("Summary Statistics")
        st.dataframe(filtered_df[['n1', 'n2', 'n3']].describe())

        # Correlation heatmap
        st.subheader("Score Correlations")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[['n1', 'n2', 'n3']].corr(), 
                   annot=True, 
                   cmap='coolwarm', 
                   ax=ax)
        plt.tight_layout()
        st.pyplot(fig)

def main():
    st.title("Survey Data Viewer")

    # Use the same DB_PATH from db_manager
    db_path = st.sidebar.text_input(
        "Database Path",
        value=DB_PATH,  # Use the same path constant
        help="Enter the path to your SQLite database"
    )

    try:
        viewer = SurveyDataViewer(db_path=db_path)

        page = st.sidebar.radio(
            "Select View",
            ["Response Analysis", "Score Distribution"]
        )

        if page == "Response Analysis":
            viewer.show_response_analysis()
        elif page == "Score Distribution":
            viewer.show_score_distribution()

        # Add debug information
        if st.sidebar.checkbox("Show Debug Info"):
            st.sidebar.text(f"Database Path: {db_path}")
            st.sidebar.text(f"Total Records: {len(viewer.responses_df)}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Error in main: {e}", exc_info=True)

if __name__ == "__main__":
    main()