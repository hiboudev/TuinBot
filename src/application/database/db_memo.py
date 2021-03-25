from dataclasses import dataclass
from typing import List, Union

from application.database.db_connexion import DatabaseConnection


@dataclass
class Memo:
    name: str
    content: str


@dataclass
class MemoListItem:
    name: str
    position: int


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
                                    name LIKE %(name)s
                                ORDER BY
                                    name
                                LIMIT 1
                                """,
                           {"author_id": author_id, "name": "%" + name + "%"})

            result = cursor.fetchone()
            return None if not result else Memo(result[0], result[1])

    @staticmethod
    def get_memo_by_position(author_id: int, position: int) -> Union[Memo, None]:
        with DatabaseConnection() as cursor:
            # cursor.execute("SET @row_number = 0;")
            cursor.execute("""
                                SELECT
                                    name,
                                    content
                                FROM
                                    memo
                                WHERE
                                    author_id = %(author_id)s
                                ORDER BY
                                    name
                                LIMIT %(position)s, 1
                                """,
                           {"author_id": author_id, "position": position - 1})

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
    def get_memo_list(author_id: int) -> List[MemoListItem]:
        with DatabaseConnection() as cursor:
            cursor.execute("SET @row_number = 0;")
            cursor.execute("""
                                SELECT
                                    name,
                                    (@row_number:=@row_number + 1) AS num
                                FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                ORDER BY
                                    name
                                """,
                           {"author_id": author_id})

            return [MemoListItem(i[0], i[1]) for i in cursor.fetchall()]

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
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                SELECT COUNT(*)
                                    FROM
                                        memo
                                    WHERE
                                        author_id = %(author_id)s
                                """,
                           {"author_id": author_id})

            return cursor.fetchone()[0]
