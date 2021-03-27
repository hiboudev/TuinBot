from dataclasses import dataclass
from typing import List, Union

from application.database.db_connexion import DatabaseConnection


@dataclass
class Memo:
    name: str
    lines: List[str]


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
                                    memo (author_id, name)
                                VALUES
                                    (%(author_id)s, %(name)s)
                               """,
                           {"author_id": author_id, "name": name})

            if cursor.rowcount == 0:
                return False

            memo_id = cursor.lastrowid

            cursor.execute("""
                                INSERT INTO
                                    memo_line (memo_id, content)
                                VALUES
                                    (%(memo_id)s, %(content)s)
                               """,
                           {"memo_id": memo_id, "content": content})

            return cursor.rowcount > 0

    @staticmethod
    def get_memo_name(author_id: int, name_part: str) -> Union[str, None]:
        with DatabaseConnection() as cursor:
            cursor.execute(f"""
                                SELECT
                                    name
                                FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                AND
                                    name LIKE %(name_part)s
                                ORDER BY
                                    name
                                LIMIT 1
                                """,
                           {"author_id": author_id, "name_part": name_part + "%"})

            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def get_memo(author_id: int, name_part: str, exact_name: bool = False) -> Union[Memo, None]:
        name_operator = "=" if exact_name else "LIKE"

        with DatabaseConnection() as cursor:
            cursor.execute(f"""
                                SELECT
                                    id,
                                    name
                                FROM
                                    memo
                                WHERE
                                    author_id=%(author_id)s
                                AND
                                    name {name_operator} %(name_part)s
                                ORDER BY
                                    name
                                LIMIT 1
                                """,
                           {"author_id": author_id,
                            "name_part": name_part if exact_name else name_part + "%"
                            })

            result = cursor.fetchone()
            if not result:
                return None

            memo_id = result[0]
            memo_name = result[1]

            cursor.execute("""
                                SELECT
                                    content
                                FROM
                                    memo_line
                                WHERE
                                    memo_id=%(memo_id)s
                                ORDER BY
                                    id
                                """,
                           {"memo_id": memo_id})

            lines = [i[0] for i in cursor.fetchall()]

            return Memo(memo_name, lines)

    @staticmethod
    def edit_memo(author_id: int, name: str, content: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                INSERT INTO
                                    memo_line (memo_id, content)
                                VALUES (
                                    (
                                        SELECT
                                            id
                                        FROM
                                            memo
                                        WHERE
                                            author_id = %(author_id)s
                                        AND
                                            name LIKE %(name)s
                                        LIMIT 1
                                    ),
                                    %(content)s)
                                """,
                           {"author_id": author_id, "name": name + "%", "content": content})

            return cursor.rowcount > 0

    @staticmethod
    def get_memo_line(author_id: int, name_part: str, line_position: int) -> Union[str, None]:
        """line_position starts at 1"""
        if line_position < 1:
            raise ValueError("line_position must be > 0")

        with DatabaseConnection() as cursor:
            cursor.execute("SET @row_number = 0;")
            cursor.execute("""
                                SELECT
                                    content
                                FROM
                                    memo_line
                                WHERE
                                    memo_id
                                        =  (
                                                SELECT
                                                    id
                                                FROM
                                                    memo
                                                WHERE
                                                    author_id = %(author_id)s
                                                AND
                                                    name LIKE %(name_part)s
                                                LIMIT 1
                                            )
                                ORDER BY
                                    id
                                LIMIT
                                    %(line_position)s, 1
                                    
                                """,
                           {"author_id": author_id, "name_part": name_part + "%",
                            "line_position": line_position - 1})

            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def remove_memo_line(author_id: int, name: str, line_position: int) -> bool:
        """line_position starts at 1"""
        if line_position < 1:
            raise ValueError("line_position must be > 0")
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE FROM
                                    memo_line
                                WHERE
                                        id =    (
                                                    SELECT  id
                                                    FROM    (
                                                                SELECT  id
                                                                FROM    memo_line
                                                                WHERE   memo_id
                                                                        IN  (
                                                                                SELECT  id
                                                                                FROM    memo
                                                                                WHERE   author_id = %(author_id)s
                                                                                AND     name = %(name)s
                                                                            )
                                                                    ORDER BY    id
                                                                    LIMIT       %(line_position)s,1
                                                            ) as t
                                                )
                                        
                                   """,
                           {"author_id": author_id, "name": name, "line_position": line_position - 1})

            return cursor.rowcount > 0

    @staticmethod
    def remove_memo(author_id: int, name: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("""
                                DELETE
                                    memo,
                                    memo_line
                                FROM
                                    memo
                                JOIN
                                    memo_line
                                        ON
                                            memo_line.memo_id = memo.id
                                WHERE
                                    memo.author_id = %(author_id)s
                                AND
                                    memo.name = %(name)s
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

    @classmethod
    def count_memo_lines(cls, author_id: int, name_part: str, exact_name: bool = False) -> int:
        name_operator = "=" if exact_name else "LIKE"

        with DatabaseConnection() as cursor:
            cursor.execute(f"""
                                SELECT COUNT(*)
                                    FROM
                                        memo_line
                                    WHERE
                                        memo_id
                                            =  (
                                                    SELECT
                                                        id
                                                    FROM
                                                        memo
                                                    WHERE
                                                        author_id = %(author_id)s
                                                    AND
                                                        name {name_operator} %(name_part)s
                                                    LIMIT 1
                                                )
                                """,
                           {"author_id": author_id,
                            "name_part": name_part if exact_name else name_part + "%"
                            })

            return cursor.fetchone()[0]
