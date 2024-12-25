Thanks for sharing the updated directory structure. Based on this layout, here's an updated README file that better reflects your project's current setup and modular structure:

---

# **TernaryChartProject**
An interactive ternary chart application designed for exploring conceptual frameworks through modern and postmodern perspectives. It provides modular components for data handling, visualization, and user interaction.

---

## **Features**
### **Main Application**
- Interactive questionnaire for collecting participant responses.
- Real-time ternary chart visualizations for intuitive feedback.
- Aggregates and analyses participant responses.

### **Data Handling** (`src/data`)
- **`data_handler.py`**: Manages database operations for storing and retrieving responses.
- **`sqlite_utils.py`**: Provides utility functions for interacting with SQLite.

### **Survey Logic** (`src/core`)
- **`survey_logic.py`**: Core logic for handling survey questions and flow.

### **Question Management** (`src/questions`)
- **`question_manager.py`**: Handles question configurations and mappings between questions and responses.

### **User Interface** (`src/ui`)
- **`streamlit_app.py`**: Streamlit-based interface for running the survey in a user-friendly environment.

### **Visualization** (`src/visualization`)
- **`ternary_plotter.py`**: Renders ternary plots for visualizing responses and scores.

### **Data Viewer** (`data_viewer`)
- **`data_viewer.py`**: Tools for response analysis, including visualizing response patterns and score distributions.

---

## **Directory Structure**
```plaintext
TernaryChartProject/
├── data_viewer/
│   ├── data_viewer.py            # Tools for response analysis
│   └── questionnaire_responses.db # SQLite database (persistent)
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── survey_logic.py       # Core survey logic
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_handler.py       # Database handling logic
│   │   ├── questions_responses.json # Sample questions and responses
│   │   └── sqlite_utils.py       # SQLite utility functions
│   ├── questions/
│   │   ├── __init__.py
│   │   └── question_manager.py   # Question management logic
│   ├── ui/
│   │   ├── __init__.py
│   │   └── streamlit_app.py      # Streamlit user interface
│   └── visualization/
│       ├── __init__.py
│       └── ternary_plotter.py    # Ternary chart plotting
├── tests/
│   ├── test_data/
│   │   ├── test_data_handler.py  # Unit tests for data_handler
│   │   └── test_sqlite_utils.py  # Unit tests for sqlite_utils
├── venv/                         # Python virtual environment
├── app.py                        # Main entry point for the application
├── questionnaire_responses.db    # Persistent database
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── CHANGELOG.md                  # Changelog for the project
└── setup.py                      # Packaging and installation script
```

---

## **Setup Instructions**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Microglyphics/TernaryChartProject.git
   cd TernaryChartProject
   ```

2. **Set Up a Virtual Environment**:
   - Create and activate the virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```

   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the Application**:
   - Use the Streamlit app for the questionnaire:
     ```bash
     streamlit run src/ui/streamlit_app.py
     ```

4. **Run Tests**:
   - Verify functionality using pytest:
     ```bash
     pytest tests/
     ```

---

## **Usage**
- **Interactive Survey**:
  - Launch the Streamlit app to run the questionnaire and visualize responses in real-time.
  
- **Response Analysis**:
  - Use `data_viewer.py` to analyze and visualize aggregated response patterns.

- **Customization**:
  - Modify `questions_responses.json` for custom survey questions and response mappings.
  - Extend functionality by adding new modules under `src/`.

---

## **Future Enhancements**
- **Expanded Visualization**:
  - Enhance the `ternary_plotter` module with advanced charting features.
- **Web Deployment**:
  - Deploy the project as a fully interactive web application.
