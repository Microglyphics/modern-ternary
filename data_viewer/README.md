# Survey Data Viewer

A Streamlit-based visualization tool for exploring the Worldview Survey questions and responses.

## Features

- Questions Overview: View and analyze individual questions and their response options
- Response Analysis: Track response patterns and download raw data
- Score Distribution: Analyze the distribution of PreModern, Modern, and PostModern scores

## Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the viewer:
```bash
streamlit run data_viewer.py
```

## Usage

The viewer provides three main views:

1. **Questions Overview**
   - Select individual questions to view
   - See response options and their scoring
   - Visualize score distributions per question

2. **Response Analysis**
   - View response counts over time
   - Download raw response data
   - See basic response statistics

3. **Score Distribution**
   - View box plots of score distributions
   - Analyze correlations between different worldview scores
   - See summary statistics

## Data Sources

The viewer reads from:
- `questions_responses.json`: Survey questions and scoring
- `survey_responses.csv`: Collected response data (if available)