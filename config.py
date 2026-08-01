import sqlite3

DATABASE_NAME = "database/database.db"


def create_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = create_connection()
    cursor = conn.cursor()

    # Doctors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        fullname TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        profile_image TEXT DEFAULT 'default-user.jpg'

    )
    """)

    # Prediction History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        doctor_name TEXT NOT NULL,

        doctor_email TEXT NOT NULL,

        patient_name TEXT NOT NULL,

        patient_age INTEGER,

        patient_gender TEXT,

        image_name TEXT NOT NULL,

        prediction TEXT NOT NULL,

        confidence REAL NOT NULL,

        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()