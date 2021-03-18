from typing import List

import mysql.connector


# Doc : https://python.doctor/page-database-data-base-donnees-query-sql-mysql-postgre-sqlite

class Database:

    @staticmethod
    def add_auto_reaction(author_id: str, target_id: str, emoji: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            INSERT INTO
                                auto_reaction (author_id, target_id, emoji)
                            VALUES
                                (%(author_id)s, %(target_id)s, %(emoji)s)
                            ON DUPLICATE KEY UPDATE
                                emoji = %(emoji)s
                           """,
                           {"author_id": author_id, "target_id": target_id, "emoji": emoji})

            return cursor.rowcount > 0

    @staticmethod
    def remove_auto_reaction(author_id: str, target_id: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            DELETE FROM
                                auto_reaction
                            WHERE
                                author_id = %(author_id)s
                            AND
                                target_id = %(target_id)s
                           """,
                           {"author_id": author_id, "target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def remove_all_auto_reactions(target_id: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            DELETE FROM
                                auto_reaction
                            WHERE
                                target_id = %(target_id)s
                           """,
                           {"target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def get_auto_reactions(user_id: str) -> List[str]:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            SELECT
                                emoji
                            FROM
                                auto_reaction
                            WHERE
                                target_id = %(user_id)s
                            """,
                           {"user_id": user_id})

            return [i[0] for i in cursor.fetchall()]


class DatabaseConnection:

    def __enter__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tuinbot"
        )

        print(self.conn)

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
