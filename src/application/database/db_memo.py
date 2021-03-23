from dataclasses import dataclass
from typing import List, Union

from application.database.db_connexion import DatabaseConnection


@dataclass
class Memo:
    name: str
    content: str


class DbMemo:

    @staticmethod
    def add_memo(author_id: int, name: str, content: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                INSERT IGNORE INTO
                                    memo (author_id, name, content)
                                VALUES
                                    (%(author_id)s, %(name)s, %(content)s)
                               """,
                           {"author_id": author_id, "name": name, "content": content})

            return cursor.rowcount > 0

    @staticmethod
    def get_memo(author_id: int, name: str) -> Union[Memo, None]:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    name,
                                    content
                                FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                AND
                                    name = %(name)s
                                """,
                           {"author_id": author_id, "name": name})

            result = cursor.fetchone()
            return None if not result else Memo(result[0], result[1])

    @staticmethod
    def remove_memo(author_id: int, name: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                AND
                                    name = %(name)s
                               """,
                           {"author_id": author_id, "name": name})

            return cursor.rowcount > 0

    @staticmethod
    def get_memo_list(author_id: int) -> List[str]:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT
                                    name
                                FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                """,
                           {"author_id": author_id})

            return [i[0] for i in cursor.fetchall()]

    @staticmethod
    def edit_memo(author_id: int, name: str, content: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                UPDATE
                                    memo
                                SET
                                    content =  %(content)s
                                WHERE
                                    author_id = %(author_id)s
                                AND
                                    name = %(name)s
                                """,
                           {"author_id": author_id, "name": name, "content": content})

            return cursor.rowcount > 0

    @classmethod
    def count_user_memos(cls, author_id: int) -> int:
        sql = """
                    SELECT COUNT(*)
                        FROM
                            memo
                        WHERE
                            author_id = %(author_id)s
                    """

        with DatabaseConnection() as cursor:
            cursor.execute(sql,
                           {"author_id": author_id})

            return cursor.fetchone()[0]
