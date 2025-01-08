import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import sys
import os
import sqlite3
from pathlib import Path  # Import Path to handle filesystem paths

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("viewer_debug.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_database_path():
    """Get the database path for both local and production environments"""
    possible_paths = [
        os.getenv("SURVEY_DB_PATH"),  # Environment variable for dynamic configuration
        '/mount/src/modern-ternary/src/data/survey_results.db',  # Production path
        'src/data/survey_results.db',  # Local development path
        '../src/data/survey_results.db',  # Relative path
        'survey_results.db',  # Same directory
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            logger.debug(f"Found database at: {path}")
            return path

    default_path = '/mount/src/modern-ternary/src/data/survey_results.db'
    logger.debug(f"Using default path: {default_path}")
    return default_path

def log_table_contents(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.debug(f"Tables in database: {tables}")

            if tables:
                first_table = tables[0][0]
                cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                records = cursor.fetchall()
                logger.debug(f"Contents of {first_table}: {records}")
    except Exception as e:
        logger.error(f"Error logging table contents: {e}", exc_info=True)

class SurveyDataViewer:
    def __init__(self, db_path: str = None):
        """Initialize viewer with database connection"""
        self.db_path = db_path or get_database_path()
        logger.debug(f"Initializing SurveyDataViewer with path: {self.db_path}")

        if not os.path.exists(self.db_path):
            error_msg = f"Database not found at: {self.db_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        self.load_data()

    def load_data(self):
        """Load response data from database"""
        log_table_contents(self.db_path)

        try:
            logger.debug("Attempting to load response data")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
                self.responses_df = pd.read_sql_query("""
                    SELECT 
                        timestamp,
                        CAST(q1_response AS INTEGER) as q1_response, 
                        CAST(q2_response AS INTEGER) as q2_response,
                        CAST(q3_response AS INTEGER) as q3_response,
                        CAST(q4_response AS INTEGER) as q4_response,
                        CAST(q5_response AS INTEGER) as q5_response,
                        CAST(q6_response AS INTEGER) as q6_response,
                        CAST(n1 AS INTEGER) as n1,
                        CAST(n2 AS INTEGER) as n2,
                        CAST(n3 AS INTEGER) as n3,
                        CAST(plot_x AS FLOAT) as plot_x,
                        CAST(plot_y AS FLOAT) as plot_y,
                        session_id,
                        source,
                        version,
                        browser,
                        region
                    FROM survey_results 
                    ORDER BY timestamp DESC
                """, conn)

            if not self.responses_df.empty:
                logger.debug(f"Loaded {len(self.responses_df)} records")
                self.responses_df['timestamp'] = pd.to_datetime(self.responses_df['timestamp'])
                logger.debug(f"DataFrame info:\n{self.responses_df.info()}")
            else:
                logger.warning("No data found in survey_results table")
                self.responses_df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading responses: {e}", exc_info=True)
            st.error(f"Error loading data: {str(e)}")
            self.responses_df = pd.DataFrame()


    def inspect_latest_records(self):
        """Inspect the most recent records in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, source, version 
                    FROM survey_results 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                records = cursor.fetchall()
                st.subheader("Latest Records")
                for record in records:
                    st.write(f"ID: {record[0]}, Time: {record[1]}, Source: {record[2]}, Version: {record[3]}")
        except Exception as e:
            logger.error(f"Error inspecting latest records: {e}", exc_info=True)
            st.error("Failed to fetch latest records.")

    def show_response_analysis(self):
        """Show response analysis"""
        st.header("Response Analysis")

        if self.responses_df.empty:
            st.warning("No response data available yet.")
            return

        st.subheader("Latest Records Details")
        self.inspect_latest_records()

        st.subheader("Response Summary")
        total_responses = len(self.responses_df)
        st.write(f"Total Responses: {total_responses}")

        if 'version' in self.responses_df.columns:
            st.subheader("Version Distribution")
            version_counts = self.responses_df['version'].value_counts()
            st.bar_chart(version_counts)

        if 'source' in self.responses_df.columns:
            st.subheader("Source Distribution")
            source_counts = self.responses_df['source'].value_counts()
            st.bar_chart(source_counts)

        st.subheader("Response Details")
        with st.expander("Filter Options"):
            col1, col2 = st.columns(2)
            with col1:
                selected_version = st.multiselect("Filter by Version", options=self.responses_df['version'].unique())
            with col2:
                selected_source = st.multiselect("Filter by Source", options=self.responses_df['source'].unique())

        filtered_df = self.responses_df
        if selected_version:
            filtered_df = filtered_df[filtered_df['version'].isin(selected_version)]
        if selected_source:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_source)]

        st.dataframe(filtered_df, height=500)

        st.subheader("Responses Over Time")
        if not filtered_df.empty:
            responses_by_day = filtered_df.resample('D', on='timestamp').size()

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

        with st.expander("Filter Options"):
            col1, col2 = st.columns(2)
            with col1:
                selected_version = st.multiselect("Filter by Version", options=self.responses_df['version'].unique())
            with col2:
                selected_source = st.multiselect("Filter by Source", options=self.responses_df['source'].unique())

        filtered_df = self.responses_df
        if selected_version:
            filtered_df = filtered_df[filtered_df['version'].isin(selected_version)]
        if selected_source:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_source)]

        st.subheader("Distribution of Scores")
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            filtered_df[['n1', 'n2', 'n3']].boxplot(ax=ax)
            ax.set_title('Score Distribution by Category')
            ax.set_ylabel('Score')
            ax.set_xticklabels(['PreModern', 'Modern', 'PostModern'])
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            st.subheader("Detailed Score Distribution")
            fig, ax = plt.subplots(figsize=(10, 6))
            score_data = pd.melt(filtered_df[['n1', 'n2', 'n3']], var_name='Category', value_name='Score')
            sns.violinplot(data=score_data, x='Category', y='Score', ax=ax)
            ax.set_xticklabels(['PreModern', 'Modern', 'PostModern'])
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            st.subheader("Summary Statistics")
            st.dataframe(filtered_df[['n1', 'n2', 'n3']].describe())

            st.subheader("Score Correlations")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(filtered_df[['n1', 'n2', 'n3']].corr(), annot=True, cmap='coolwarm', ax=ax)
            plt.tight_layout()
            st.pyplot(fig)

def main():
    st.title("Survey Data Viewer")

    # Add a refresh cache button
    if st.button("🔄 Refresh Cache"):
        st.cache_data.clear()  # Clear the cache for fresh data load
        try:
            viewer = SurveyDataViewer(db_path=get_database_path())
            st.success("Cache cleared and data reloaded!")
        except Exception as e:
            st.error(f"Error reloading data: {e}")
            logger.error(f"Error during cache refresh: {e}", exc_info=True)

    st.sidebar.markdown("### Environment Information")
    st.sidebar.text(f"Current working directory: {os.getcwd()}")

    default_db_path = get_database_path()
    st.sidebar.markdown("### Database Configuration")
    st.sidebar.text("Current database path:")
    st.sidebar.text(default_db_path)

    try:
        viewer = SurveyDataViewer(db_path=default_db_path)

        page = st.sidebar.radio("Select View", ["Response Analysis", "Score Distribution"])

        if page == "Response Analysis":
            viewer.show_response_analysis()
        elif page == "Score Distribution":
            viewer.show_score_distribution()

        if st.sidebar.checkbox("Show Debug Info"):
            st.sidebar.json({
                "Database Path": default_db_path,
                "Database Exists": os.path.exists(default_db_path),
                "Total Records": len(viewer.responses_df),
                "Current Directory": os.getcwd(),
                "Python Path": sys.path
            })

    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Error in main: {e}", exc_info=True)

        with st.expander("Error Details"):
            st.write("Current working directory:", os.getcwd())
            st.write("Python path:", sys.path)
            st.write("Attempted database path:", default_db_path)
            if os.path.exists(default_db_path):
                st.write("✅ Database file exists")
                try:
                    with sqlite3.connect(default_db_path) as conn:
                        conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = cursor.fetchall()
                        st.write("Tables in database:", tables)
                except Exception as db_error:
                    st.write("❌ Error accessing database:", str(db_error))
            else:
                st.write("❌ Database file not found")

if __name__ == "__main__":
    main()
