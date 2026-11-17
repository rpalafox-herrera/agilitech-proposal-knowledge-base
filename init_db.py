"""Run once (or safely repeat): python init_db.py."""
from kb.service import KnowledgeBase

if __name__ == "__main__":
    kb = KnowledgeBase()
    print(f"Database ready: {kb.db_path}")
    print("SQLite FTS5 and persistent local storage initialized.")
