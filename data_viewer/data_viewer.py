import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
import sqlite3
import json
from src.data.sqlite_utils import SQLiteManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def inspect_database_content():
    """Debug function to inspect database content"""
    conn = sqlite3.connect('questionnaire_responses.db')
    cursor = conn.cursor()
    
    output = []
    output.append("\n=== Database Inspection ===")
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    output.append(f"\nTables found: {tables}")
    
    try:
        # Check responses table content
        cursor.execute("SELECT * FROM responses")
        rows = cursor.fetchall()
        
        if not rows:
            output.append("No rows found in responses table")
            return "\n".join(output)
        
        # Get column names
        cursor.execute("PRAGMA table_info(responses)")
        columns = [col[1] for col in cursor.fetchall()]
        output.append(f"\nColumns: {columns}")
        
        # Print each row nicely formatted
        for row in rows:
            output.append("\n--- Row ---")
            for col, val in zip(columns, row):
                output.append(f"{col}: {val}")
                if col in ['responses', 'scores', 'aggregate_response']:
                    try:
                        parsed = json.loads(val)
                        output.append(f"Parsed {col}: {json.dumps(parsed, indent=2)}")
                    except json.JSONDecodeError as e:
                        output.append(f"Error parsing {col}: {e}")
                        output.append(f"Raw value: {val}")
    except Exception as e:
        output.append(f"Error inspecting database: {e}")
    finally:
        conn.close()
        
    return "\n".join(output)

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
                self.responses_df = pd.read_sql_query("SELECT * FROM survey_results", conn)
            
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

        st.subheader("Response Summary")
        st.write(f"Total Responses: {len(self.responses_df)}")
        st.dataframe(self.responses_df, height=500)  # Adjust height as needed

        st.subheader("Responses Over Time")
        if 'timestamp' in self.responses_df.columns:
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

        # Score distribution
        st.subheader("Distribution of Scores (n1, n2, n3)")
        fig, ax = plt.subplots(figsize=(10, 6))
        self.responses_df[['n1', 'n2', 'n3']].boxplot(ax=ax)
        ax.set_title('Score Distribution by Category')
        ax.set_ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig)

        # Summary statistics
        st.subheader("Summary Statistics")
        st.dataframe(self.responses_df[['n1', 'n2', 'n3']].describe())

    def inspect_database_content():
        """Debug function to inspect database content"""
        conn = sqlite3.connect('questionnaire_responses.db')
        cursor = conn.cursor()
        
        output = []
        output.append("\n=== Database Inspection ===")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        output.append(f"\nTables found: {tables}")
        
        # Check responses table content
        cursor.execute("SELECT * FROM responses")
        rows = cursor.fetchall()
        
        if not rows:
            output.append("No rows found in responses table")
            return "\n".join(output)
        
        # Get column names
        cursor.execute("PRAGMA table_info(responses)")
        columns = [col[1] for col in cursor.fetchall()]
        output.append(f"\nColumns: {columns}")
        
        # Print each row nicely formatted
        for row in rows:
            output.append("\n--- Row ---")
            for col, val in zip(columns, row):
                output.append(f"{col}: {val}")
                if col in ['responses', 'scores', 'aggregate_response']:
                    try:
                        parsed = json.loads(val)
                        output.append(f"Parsed {col}: {json.dumps(parsed, indent=2)}")
                    except json.JSONDecodeError as e:
                        output.append(f"Error parsing {col}: {e}")
                        output.append(f"Raw value: {val}")
        
        conn.close()
        return "\n".join(output)
    
    # In data_viewer/data_viewer.py, add as a function outside the class
    def inspect_database_content():
        """Debug function to inspect database content"""
        conn = sqlite3.connect('questionnaire_responses.db')
        cursor = conn.cursor()
        
        output = []
        output.append("\n=== Database Inspection ===")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        output.append(f"\nTables found: {tables}")
        
        try:
            # Check responses table content
            cursor.execute("SELECT * FROM responses")
            rows = cursor.fetchall()
            
            if not rows:
                output.append("No rows found in responses table")
                return "\n".join(output)
            
            # Get column names
            cursor.execute("PRAGMA table_info(responses)")
            columns = [col[1] for col in cursor.fetchall()]
            output.append(f"\nColumns: {columns}")
            
            # Print each row nicely formatted
            for row in rows:
                output.append("\n--- Row ---")
                for col, val in zip(columns, row):
                    output.append(f"{col}: {val}")
                    if col in ['responses', 'scores', 'aggregate_response']:
                        try:
                            parsed = json.loads(val)
                            output.append(f"Parsed {col}: {json.dumps(parsed, indent=2)}")
                        except json.JSONDecodeError as e:
                            output.append(f"Error parsing {col}: {e}")
                            output.append(f"Raw value: {val}")
        except Exception as e:
            output.append(f"Error inspecting database: {e}")
        finally:
            conn.close()
            
        return "\n".join(output)

    # Make sure inspect_database_content is defined BEFORE main()

def main():
    st.title("Survey Data Viewer")

    try:
        viewer = SurveyDataViewer(db_path='src/data/survey_results.db')

        page = st.sidebar.radio(
            "Select View",
            ["Response Analysis", "Score Distribution"]
        )

        if page == "Response Analysis":
            viewer.show_response_analysis()
        elif page == "Score Distribution":
            viewer.show_score_distribution()

    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Error in main: {e}", exc_info=True)

if __name__ == "__main__":
    main()
