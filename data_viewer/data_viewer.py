import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import sys
import os
import sqlite3
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_database_path():
    """Get the database path for both local and production environments"""
    # Try possible database locations
    possible_paths = [
        '/mount/src/modern-ternary/src/data/survey_results.db',  # Production path
        'src/data/survey_results.db',  # Local development path
        '../src/data/survey_results.db',  # Relative path
        'survey_results.db',  # Same directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.debug(f"Found database at: {path}")
            return path
            
    # Default to the production path even if it doesn't exist yet
    default_path = '/mount/src/modern-ternary/src/data/survey_results.db'
    logger.debug(f"Using default path: {default_path}")
    return default_path

class SurveyDataViewer:
    def __init__(self, db_path: str = None):
        """Initialize viewer with database connection"""
        self.db_path = db_path or get_database_path()
        logger.debug(f"Initializing SurveyDataViewer with path: {self.db_path}")
        
        # Verify database existence
        if not os.path.exists(self.db_path):
            error_msg = f"Database not found at: {self.db_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        self.load_data()

    def load_data(self):
        """Load response data from database"""
        try:
            logger.debug("Attempting to load response data")
            with sqlite3.connect(self.db_path) as conn:
                # Log the tables in the database
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                logger.debug(f"Tables in database: {tables}")
                
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
    
    # Show environment information
    st.sidebar.markdown("### Environment Information")
    st.sidebar.text(f"Current working directory: {os.getcwd()}")
    
    # Get default database path
    default_db_path = get_database_path()
    
    # Database path input with current path display
    st.sidebar.markdown("### Database Configuration")
    st.sidebar.text("Current database path:")
    st.sidebar.text(default_db_path)
    
    try:
        viewer = SurveyDataViewer(db_path=default_db_path)

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
        
        # Show additional error information
        with st.expander("Error Details"):
            st.write("Current working directory:", os.getcwd())
            st.write("Python path:", sys.path)
            st.write("Attempted database path:", default_db_path)
            if os.path.exists(default_db_path):
                st.write("✅ Database file exists")
                try:
                    with sqlite3.connect(default_db_path) as conn:
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