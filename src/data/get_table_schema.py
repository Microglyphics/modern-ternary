python -c "
import sqlite3
conn = sqlite3.connect('survey_results.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(responses);')
print(cursor.fetchall())
conn.close()
"
