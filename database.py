import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

from nlp import compute_sentiment, extract_themes

DB_PATH = "journal_entries.db"

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            text TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            sentiment_label TEXT NOT NULL,
            themes TEXT NOT NULL
        )
        """
    )
    
    return connection

def save_entry(text: str) -> None:
    sentiment_score, sentiment_label = compute_sentiment(text)
    themes = extract_themes(text)
    created_at = datetime.now(timezone.utc).isoformat()

    connection = get_connection()
    connection.execute(
        """
        INSERT INTO journal_entries (created_at, text, sentiment_score, sentiment_label, themes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (created_at, text, sentiment_score, sentiment_label, ",".join(themes)),
    )
    connection.commit()
    connection.close()

def load_entries(days: Optional[int] = None) -> List[Dict]:
    connection = get_connection()
    cursor = connection.cursor()

    if days is None:
        cursor.execute(
            """
            SELECT id, created_at, text, sentiment_score, sentiment_label, themes
            FROM journal_entries
            ORDER BY created_at
            """
        )
        rows = cursor.fetchall()

    else:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cursor.execute(
            """
            SELECT id, created_at, text, sentiment_score, sentiment_label, themes
            FROM journal_entries
            WHERE created_at >= ?
            ORDER BY created_at
            """,
            (cutoff,),
        )
        rows = cursor.fetchall()
    
    connection.close()

    entries: List[Dict] = []
    for rowId, created_at, text, score, label, theme_str in rows:
        entries.append(
            {
                "id": rowId,
                "created_at": created_at,
                "text": text,
                "sentiment_score": score,
                "sentiment_label": label,
                "themes": theme_str.split(",") if theme_str else [],
            }
        )
    return entries