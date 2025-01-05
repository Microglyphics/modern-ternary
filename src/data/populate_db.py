import os
import sqlite3
import json

# Construct paths
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "survey_results.db")
json_path = os.path.join(base_dir, "questions_responses.json")

# Load JSON data
with open(json_path, "r") as f:
    data = json.load(f)
questions_data = data["questions"]

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS responses (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    text TEXT NOT NULL,
    scores TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions (id)
);
""")

# Insert data into tables
for question_id, question_info in questions_data.items():
    # Insert question
    cursor.execute("""
        INSERT OR IGNORE INTO questions (id, text)
        VALUES (?, ?)
    """, (question_id, question_info["text"]))

    # Insert responses
    for response in question_info["responses"]:
        cursor.execute("""
            INSERT OR IGNORE INTO responses (id, question_id, text, scores)
            VALUES (?, ?, ?, ?)
        """, (response["id"], question_id, response["text"], json.dumps(response["scores"])))

# Commit and close
conn.commit()
conn.close()

print("Data inserted successfully.")
