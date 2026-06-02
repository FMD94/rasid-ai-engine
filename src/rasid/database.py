import sqlite3
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

DB_PATH = Path("logs/rasid.db")
DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_column(cursor, table_name: str, column_name: str, column_type: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        input_type TEXT,
        decision TEXT,
        language TEXT,
        confidence REAL,
        reasons TEXT,
        lime_explanation TEXT,
        explanation TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS moderator_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_timestamp TEXT,
        analysis_id INTEGER,
        ai_decision TEXT,
        final_decision TEXT,
        language TEXT,
        input_type TEXT,
        confidence REAL,
        note TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispute_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        username TEXT,
        ad_text TEXT,
        ai_decision TEXT,
        confidence REAL,
        language TEXT,
        reasons TEXT,
        user_note TEXT,
        status TEXT
    )
    """)

    ensure_column(cursor, "analysis_logs", "lime_explanation", "TEXT")
    ensure_column(cursor, "analysis_logs", "explanation", "TEXT")

    conn.commit()
    conn.close()


def save_analysis_to_db(result: dict, source: str = "api"):
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analysis_logs (
        timestamp, source, input_type, decision, language,
        confidence, reasons, lime_explanation, explanation
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        source,
        result.get("input_type", "unknown"),
        result.get("decision", "unknown"),
        result.get("language", "unknown"),
        result.get("confidence", None),
        json.dumps(result.get("reasons", []), ensure_ascii=False),
        json.dumps(result.get("lime_explanation", []), ensure_ascii=False),
        result.get("explanation", "")
    ))

    conn.commit()
    conn.close()


def save_review_to_db(review: dict):
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO moderator_reviews (
        review_timestamp, analysis_id, ai_decision, final_decision,
        language, input_type, confidence, note
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review.get("review_timestamp", datetime.now().isoformat(timespec="seconds")),
        review.get("analysis_id", None),
        review.get("ai_decision", "unknown"),
        review.get("final_decision", "unknown"),
        review.get("language", "unknown"),
        review.get("input_type", "unknown"),
        review.get("confidence", None),
        review.get("note", "")
    ))

    conn.commit()
    conn.close()


def load_analysis_df():
    init_db()

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM analysis_logs ORDER BY id ASC",
        conn
    )

    conn.close()
    return df


def load_reviews_df():
    init_db()

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM moderator_reviews ORDER BY id ASC",
        conn
    )

    conn.close()
    return df


def load_disputes():
    init_db()

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM dispute_requests ORDER BY id DESC",
        conn
    )

    conn.close()
    return df