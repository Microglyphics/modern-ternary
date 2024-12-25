import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import ast
import os

class SurveyDataViewer:
    def __init__(self):
        # Get the parent directory path
        self.parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construct full paths to data files
        self.questions_path = os.path.join(self.parent_dir, 'questions_responses.json')
        self.responses_path = os.path.join(self.parent_dir, 'survey_responses.csv')
        
        # Set up the plotting style
        sns.set_theme()
        self.load_data()

    def load_data(self):
        # Load questions data
        with open(self.questions_path, 'r') as file:
            self.questions_data = json.load(file)
        
        # Convert questions to DataFrame for viewing
        self.questions_df = self.questions_to_df()
        
        # Load responses if they exist
        try:
            self.responses_df = pd.read_csv(self.responses_path)
            # Convert stored string representations back to Python objects
            self.responses_df['responses'] = self.responses_df['responses'].apply(ast.literal_eval)
            self.responses_df['scores'] = self.responses_df['scores'].apply(ast.literal_eval)
            self.responses_df['avg_score'] = self.responses_df['avg_score'].apply(ast.literal_eval)
        except FileNotFoundError:
            self.responses_df = pd.DataFrame()

    def questions_to_df(self) -> pd.DataFrame:
        rows = []
        for q_key, q_data in self.questions_data['questions'].items():
            for i, response in enumerate(q_data['responses']):
                rows.append({
                    'question_key': q_key,
                    'question_text': q_data['text'],
                    'response_option': i + 1,
                    'response_text': response['text'],
                    'premodern_score': response['scores'][0],
                    'modern_score': response['scores'][1],
                    'postmodern_score': response['scores'][2]
                })
        return pd.DataFrame(rows)

    def run(self):
        st.title("Survey Data Explorer")
        
        # Sidebar navigation
        page = st.sidebar.radio(
            "Select View",
            ["Questions Overview", "Response Analysis", "Score Distribution"]
        )
        
        if page == "Questions Overview":
            self.show_questions_overview()
        elif page == "Response Analysis":
            self.show_response_analysis()
        else:
            self.show_score_distribution()

    def show_questions_overview(self):
        st.header("Questions and Response Options")
        
        # Question selector
        selected_question = st.selectbox(
            "Select Question",
            self.questions_df['question_key'].unique(),
            format_func=lambda x: f"{x}: {self.questions_data['questions'][x]['text']}"
        )
        
        # Show response options for selected question
        q_data = self.questions_df[self.questions_df['question_key'] == selected_question]
        
        # Display as a more readable table
        st.subheader("Response Options and Scores")
        display_df = q_data[['response_option', 'response_text', 
                            'premodern_score', 'modern_score', 'postmodern_score']]
        st.dataframe(display_df)
        
        # Visualize score distribution for this question
        st.subheader("Score Distribution by Response Option")
        plt.figure(figsize=(10, 6))
        x = range(len(display_df))
        width = 0.25
        
        plt.bar([i - width for i in x], display_df['premodern_score'], 
                width, label='PreModern', alpha=0.7)
        plt.bar([i for i in x], display_df['modern_score'], 
                width, label='Modern', alpha=0.7)
        plt.bar([i + width for i in x], display_df['postmodern_score'], 
                width, label='PostModern', alpha=0.7)
        
        plt.xlabel('Response Option')
        plt.ylabel('Score')
        plt.title(f'Score Distribution for {selected_question}')
        plt.xticks(x, display_df['response_option'])
        plt.legend()
        plt.tight_layout()
        
        st.pyplot(plt)
        plt.close()

    def show_response_analysis(self):
        st.header("Response Analysis")
        
        if self.responses_df.empty:
            st.warning("No response data available yet.")
            return
        
        # Show basic statistics
        st.subheader("Response Summary")
        st.write(f"Total Responses: {len(self.responses_df)}")
        
        # Time-based analysis
        st.subheader("Responses Over Time")
        self.responses_df['timestamp'] = pd.to_datetime(self.responses_df['timestamp'])
        responses_by_day = self.responses_df.resample('D', on='timestamp').size()
        
        plt.figure(figsize=(10, 6))
        responses_by_day.plot()
        plt.xlabel('Date')
        plt.ylabel('Number of Responses')
        plt.title('Daily Response Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(plt)
        plt.close()
        
        # Show raw data with option to download
        st.subheader("Raw Response Data")
        if st.checkbox("Show raw data"):
            st.dataframe(self.responses_df)
            
        csv = self.responses_df.to_csv(index=False)
        st.download_button(
            label="Download response data as CSV",
            data=csv,
            file_name="survey_responses_export.csv",
            mime="text/csv"
        )

    def show_score_distribution(self):
        st.header("Score Distribution Analysis")
        
        if self.responses_df.empty:
            st.warning("No response data available yet.")
            return
        
        # Extract average scores
        avg_scores = pd.DataFrame([
            {'PreModern': s[0], 'Modern': s[1], 'PostModern': s[2]}
            for s in self.responses_df['avg_score']
        ])
        
        # Overall distribution
        st.subheader("Distribution of Average Scores")
        plt.figure(figsize=(10, 6))
        avg_scores.boxplot()
        plt.title('Distribution of Scores by Category')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(plt)
        plt.close()
        
        # Score correlations using seaborn's pairplot
        st.subheader("Score Correlations")
        pair_plot = sns.pairplot(avg_scores)
        st.pyplot(pair_plot.fig)
        plt.close()
        
        # Summary statistics
        st.subheader("Summary Statistics")
        st.dataframe(avg_scores.describe())

if __name__ == "__main__":
    viewer = SurveyDataViewer()
    viewer.run()