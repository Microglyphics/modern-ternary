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
