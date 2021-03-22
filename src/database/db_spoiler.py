from typing import Union

from database.db_connexion import DatabaseConnection


class DbAutoSpoiler:

    @staticmethod
    def add_auto_spoiler(guild_id: int, author_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                            INSERT IGNORE INTO
                                auto_spoiler (guild_id, author_id, target_id)
                            VALUES
                                (%(guild_id)s, %(author_id)s, %(target_id)s)
                           """,
                           {"guild_id": guild_id, "author_id": author_id, "target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def remove_auto_spoiler(guild_id: int, author_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_spoiler
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
    def get_auto_spoiler_author(guild_id: int, target_id: int) -> Union[int, None]:
        """Doesn't delete the spoiler from database."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    author_id
                                FROM
                                    auto_spoiler
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(target_id)s
                                """,
                           {"guild_id": guild_id, "target_id": target_id})

            result = cursor.fetchone()
            return None if not result else result[0]

    @classmethod
    def use_auto_spoiler(cls, guild_id: int, target_id: int) -> Union[int, None]:
        """Delete the spoiler from database."""

        author_id = cls.get_auto_spoiler_author(guild_id, target_id)

        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_spoiler
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                """,
                           {"guild_id": guild_id, "user_id": target_id})

            return author_id
