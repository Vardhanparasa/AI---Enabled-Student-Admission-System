import sqlite3

conn = sqlite3.connect("admission.db")
cursor = conn.cursor()

# ---------------- STUDENTS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ---------------- APPLICATIONS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications(

    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    student_name TEXT,
    student_email TEXT,
    age INTEGER,
    gender TEXT,
    category TEXT,
    state TEXT,
    preferred_stream TEXT,
    entrance_exam TEXT,
    entrance_score INTEGER,
    board_percentage REAL,
    extracurricular_score INTEGER,
    scholarship_eligibility TEXT,
    ai_prediction TEXT,
    final_status TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")