import sqlite3


class CallbackInjector:

    DB_PATH = "data/improvement_history.db"

    def get_recent_topics(self, limit=3):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT video_id
        FROM pattern_success
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [r[0] for r in rows]

    def inject(self, script: str) -> str:
        callbacks = self.get_recent_topics()

        if not callbacks:
            return script

        callback_line = (
            f"\n\nAs we explored in {callbacks[0]}, "
            f"this pattern is part of a larger shift."
        )

        return script + callback_line
