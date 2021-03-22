import mysql.connector

from data.properties import AppProperties


class DatabaseConnection:
    # Doc mysql python : https://python.doctor/page-database-data-base-donnees-query-sql-mysql-postgre-sqlite

    def __enter__(self):
        self.conn = mysql.connector.connect(
            host=AppProperties.db_host(),
            user=AppProperties.db_user(),
            password=AppProperties.db_password(),
            database=AppProperties.db_name(),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
