# Modern Ternary

**Modern Ternary** is an interactive web-based questionnaire that visualises responses on a ternary chart. It explores conceptual frameworks related to Modern, Postmodern, and PreModern perspectives by aggregating and plotting user responses.

## Features
- **Dynamic Questionnaire**: Randomised response options for unbiased input.
- **Ternary Chart Visualisation**: Displays individual and aggregated results on a ternary plot.
- **Anonymised Data Capture**: Stores responses securely for future analysis.
- **Customisable Framework**: Extendable with additional questions, responses, and result explanations.

## Getting Started

### Prerequisites
- Python 3.7+
- Required Python packages:
  - `streamlit`
  - `matplotlib`
  - `ternary`
  - `sqlite3` (built into Python)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/modern-ternary.git
   cd modern-ternary
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Open the app in your browser at `http://localhost:8501`.

## Usage
1. Complete the questionnaire by selecting responses for each question.
2. Submit your responses to generate a ternary chart.
3. View your individual scores and aggregated results plotted on the chart.
4. Explore detailed explanations of the results.

## Project Structure
- `app.py`: Main Streamlit app script.
- `responses.db`: SQLite database for storing anonymised responses.
- `requirements.txt`: List of Python dependencies.

## Roadmap
- [ ] Add more questions and responses.
- [ ] Randomise question order (optional).
- [ ] Improve result explanations.
- [ ] Deploy on Streamlit Cloud for public access.
- [ ] Add data export functionality.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your proposed changes.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.