from typing import List

from application.database.db_connexion import DatabaseConnection


class DbAutoReaction:
    @staticmethod
    def add_auto_reaction(guild_id: int, channel_id: int, author_id: int, target_id: int, emoji: str,
                          shots: int) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                INSERT INTO
                                    auto_reaction (guild_id, channel_id, author_id, target_id, emoji, remaining)
                                VALUES (
                                    %(guild_id)s,
                                    %(channel_id)s,
                                    %(author_id)s,
                                    %(target_id)s,
                                    %(emoji)s,
                                    %(remaining)s
                                    )
                                ON DUPLICATE KEY UPDATE
                                    emoji = %(emoji)s,
                                    channel_id = %(channel_id)s
                               """,
                           {"guild_id": guild_id, "channel_id": channel_id, "author_id": author_id,
                            "target_id": target_id, "emoji": emoji, "remaining": shots})

            return cursor.rowcount > 0

    @staticmethod
    def reaction_exists(guild_id: int, channel_id: int, target_id: int, emoji: str) -> bool:
        """ Notes:
        - using "SELECT EXISTS" crashes on Debian 10 cause of utf-8 decoding,
        looks like it's the python connector fault.
        - the emoji comparison requests mysql table to use "COLLATE utf8mb4_bin".
        """
        sql = """
                    SELECT 1
                        FROM
                            auto_reaction
                        WHERE
                            guild_id = %(guild_id)s
                        AND
                            channel_id = %(channel_id)s
                        AND
                            target_id = %(target_id)s
                        AND
                            emoji = %(emoji)s
                        LIMIT 1
                    """

        with DatabaseConnection() as cursor:
            cursor.execute(sql,
                           {"guild_id": guild_id, "channel_id": channel_id, "target_id": target_id, "emoji": emoji})

            return cursor.fetchone() is not None

    @classmethod
    def count_total_target_reactions(cls, guild_id: int, target_id: int, exclude_user_id: int = None) -> int:
        sql = """
                    SELECT COUNT(*)
                        FROM
                            auto_reaction
                        WHERE
                            guild_id = %(guild_id)s
                        AND
                            target_id = %(target_id)s
                    """

        if exclude_user_id is not None:
            sql += """
                    AND
                        author_id != %(exclude_user_id)s
                    """

        with DatabaseConnection() as cursor:
            cursor.execute(sql,
                           {"guild_id": guild_id, "target_id": target_id, "exclude_user_id": exclude_user_id})

            return cursor.fetchone()[0]

    @classmethod
    def count_channel_target_reactions(cls, guild_id: int, channel_id: int, target_id: int) -> int:
        sql = """
                    SELECT COUNT(*)
                        FROM
                            auto_reaction
                        WHERE
                            guild_id = %(guild_id)s
                        AND
                            channel_id = %(channel_id)s
                        AND
                            target_id = %(target_id)s
                    """

        with DatabaseConnection() as cursor:
            cursor.execute(sql,
                           {"guild_id": guild_id, "channel_id": channel_id, "target_id": target_id})

            return cursor.fetchone()[0]

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
    def get_auto_reactions(guild_id: int, user_id: int, channel_id: int = None) -> List[str]:
        sql = """
                                SELECT
                                    emoji
                                FROM
                                    auto_reaction
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                """

        if channel_id is not None:
            sql += """
                                AND
                                    channel_id = %(channel_id)s
            """

        with DatabaseConnection() as cursor:
            cursor.execute(sql,
                           {"guild_id": guild_id, "channel_id": channel_id, "user_id": user_id})

            return [i[0] for i in cursor.fetchall()]

    @staticmethod
    def use_auto_reactions(guild_id: int, user_id: int, channel_id: int = None) -> List[str]:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    emoji
                                FROM
                                    auto_reaction
                                WHERE
                                    guild_id = %(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                AND
                                    channel_id = %(channel_id)s
                                """,
                           {"guild_id": guild_id, "channel_id": channel_id, "user_id": user_id})

            reactions = [i[0] for i in cursor.fetchall()]

            cursor.execute("""
                                UPDATE
                                    auto_reaction
                                SET
                                    remaining = remaining - 1
                                WHERE
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                AND
                                    channel_id = %(channel_id)s
                                """,
                           {"guild_id": guild_id, "channel_id": channel_id, "user_id": user_id})

            cursor.execute("""
                                DELETE FROM
                                    auto_reaction
                                WHERE
                                    remaining = 0
                                AND
                                    guild_id=%(guild_id)s
                                AND
                                    target_id = %(user_id)s
                                AND
                                    channel_id = %(channel_id)s
                                """,
                           {"guild_id": guild_id, "channel_id": channel_id, "user_id": user_id})

            return reactions
