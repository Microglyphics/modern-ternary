# modern-ternary
Interactive ternary chart questionnaire for exploring conceptual frameworks and aggregating responses, with modern and postmodern perspectives.

## Components

### Main Survey Application
- Interactive questionnaire
- Real-time ternary chart visualization
- Response aggregation

### Data Viewer (/data_viewer)
- Question and response analysis
- Response pattern visualization
- Score distribution analytics

## Setup
```bash
pip install -r requirements.txt
```

## Usage
Run the main survey:
```bash
streamlit run app.py
```

Analyze data (after collecting responses):
```bash
cd data_viewer
streamlit run data_viewer.py
```