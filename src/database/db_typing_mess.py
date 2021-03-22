from dataclasses import dataclass
from typing import Union, List

from database.db_connexion import DatabaseConnection


@dataclass
class TypingMessage:
    message: str
    author_id: int


class DbTypingMessage:

    @staticmethod
    def add_typing_message(guild_id: int, author_id: int, target_id: int, message: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            INSERT IGNORE INTO
                                typing_message (guild_id, author_id, target_id, message)
                            VALUES
                                (%(guild_id)s, %(author_id)s, %(target_id)s, %(message)s)
                            ON DUPLICATE KEY UPDATE
                                message = %(message)s
                           """,
                           {"guild_id": guild_id, "author_id": author_id, "target_id": target_id, "message": message})

            return cursor.rowcount > 0

    @staticmethod
    def count_typing_messages(guild_id: int, target_id: int) -> int:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    COUNT(*)
                                FROM
                                    typing_message
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "target_id": target_id})

            return cursor.fetchone()[0]

    @staticmethod
    def remove_typing_message(guild_id: int, author_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    typing_message
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
    def get_typing_message_content(guild_id: int, author_id: int, target_id: int) -> Union[str, None]:
        """Doesn't delete the spoiler from database."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    message
                                FROM
                                    typing_message
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    author_id = %(author_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "author_id": author_id, "target_id": target_id})

            result = cursor.fetchone()
            return None if not result else result[0]

    @classmethod
    def use_typing_messages(cls, guild_id: int, target_id: int) -> List[TypingMessage]:
        """Delete the spoiler from database."""

        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    message, author_id
                                FROM
                                    typing_message
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "target_id": target_id})

            messages = [TypingMessage(i[0], i[1]) for i in cursor.fetchall()]

            cursor.execute("""
                                DELETE FROM
                                    typing_message
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "target_id": target_id})

            return messages
