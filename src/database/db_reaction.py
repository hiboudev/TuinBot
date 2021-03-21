from typing import List

from database.db_connexion import DatabaseConnection


class DbAutoReaction:
    @staticmethod
    def add_auto_reaction(guild_id: int, author_id: int, target_id: int, emoji: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                INSERT INTO
                                    auto_reaction (guild_id, author_id, target_id, emoji)
                                VALUES
                                    (%(guild_id)s, %(author_id)s, %(target_id)s, %(emoji)s)
                                ON DUPLICATE KEY UPDATE
                                    emoji = %(emoji)s
                               """,
                           {"guild_id": guild_id, "author_id": author_id, "target_id": target_id, "emoji": emoji})

            return cursor.rowcount > 0

    @staticmethod
    def remove_auto_reaction(guild_id: int, author_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_reaction
                                WHERE
                                    guild_id = %(guild_id)s
                                AND
                                    author_id = %(author_id)s
                                AND
                                    target_id = %(target_id)s
                               """,
                           {"guild_id": guild_id, "author_id": author_id, "target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def remove_all_auto_reactions(guild_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_reaction
                                WHERE
                                    guild_id = %(guild_id)s
                                AND
                                    target_id = %(target_id)s
                               """,
                           {"guild_id": guild_id, "target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def get_auto_reactions(guild_id: int, user_id: int) -> List[str]:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    emoji
                                FROM
                                    auto_reaction
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                """,
                           {"guild_id": guild_id, "user_id": user_id})

            return [i[0] for i in cursor.fetchall()]
