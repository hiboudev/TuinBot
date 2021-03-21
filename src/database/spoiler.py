from database.connexion import DatabaseConnection


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
    def remove_my_spoiler(guild_id: int, target_id: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_spoiler
                                WHERE
                                    guild_id = %(guild_id)s
                                AND
                                    target_id = %(target_id)s
                               """,
                           {"guild_id": guild_id, "target_id": target_id})

            return cursor.rowcount > 0

    @staticmethod
    def get_auto_spoiler(guild_id: int, user_id: int) -> bool:
        """Doesn't delete the spoiler from database."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT EXISTS(
                                SELECT
                                    *
                                FROM
                                    auto_spoiler
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                )
                                """,
                           {"guild_id": guild_id, "user_id": user_id})

            return cursor.fetchone()[0] == 1

    @staticmethod
    def use_auto_spoiler(guild_id: int, user_id: int) -> bool:
        """Delete the spoiler from database."""

        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    auto_spoiler
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                """,
                           {"guild_id": guild_id, "user_id": user_id})

            return cursor.rowcount > 0
