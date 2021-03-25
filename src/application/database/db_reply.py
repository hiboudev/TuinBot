from dataclasses import dataclass
from typing import Union, List

from application.database.db_connexion import DatabaseConnection


@dataclass
class AutoReply:
    message: str
    author_id: int


class DbAutoReply:

    @staticmethod
    def add_auto_reply(guild_id: int, channel_id: int, author_id: int, target_id: int, message: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            INSERT IGNORE INTO
                                auto_reply (guild_id, channel_id, author_id, target_id, message)
                            VALUES (
                                %(guild_id)s,
                                %(channel_id)s,
                                %(author_id)s,
                                %(target_id)s,
                                %(message)s
                            )
                            ON DUPLICATE KEY UPDATE
                                channel_id = %(channel_id)s,
                                message = %(message)s
                           """,
                           {"guild_id": guild_id, "channel_id": channel_id, "author_id": author_id,
                            "target_id": target_id, "message": message})

            return cursor.rowcount > 0

    @staticmethod
    def count_auto_replys(guild_id: int, target_id: int, exclude_user_id: int = None) -> int:
        with DatabaseConnection() as cursor:
            sql = """
                        SELECT
                            COUNT(*)
                        FROM
                            auto_reply
                        WHERE
                            guild_id=%(guild_id)s
                        AND
                            target_id = %(target_id)s
                        """

            if exclude_user_id is not None:
                sql += """
                        AND
                            author_id != %(exclude_user_id)s
                        """

            cursor.execute(sql,
                           {"guild_id": guild_id, "target_id": target_id, "exclude_user_id": exclude_user_id})

            return cursor.fetchone()[0]

    @staticmethod
    def remove_auto_reply(guild_id: int, author_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_reply
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
    def get_auto_reply_content(guild_id: int, author_id: int, target_id: int) -> Union[str, None]:
        """Doesn't delete the spoiler from database."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    message
                                FROM
                                    auto_reply
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
    def use_auto_replys(cls, guild_id: int, channel_id: int, target_id: int) -> List[AutoReply]:
        """Delete the spoiler from database."""

        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    message, author_id
                                FROM
                                    auto_reply
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    channel_id=%(channel_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "channel_id": channel_id, "target_id": target_id})

            messages = [AutoReply(i[0], i[1]) for i in cursor.fetchall()]

            cursor.execute("""
                                DELETE FROM
                                    auto_reply
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    channel_id=%(channel_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "channel_id": channel_id, "target_id": target_id})

            return messages
