import mysql.connector

# Doc mysql python : https://python.doctor/page-database-data-base-donnees-query-sql-mysql-postgre-sqlite
from data.properties import AppProperties


class DatabaseConnection:

    def __enter__(self):
        self.conn = mysql.connector.connect(
            host=AppProperties.db_host(),
            user=AppProperties.db_user(),
            password=AppProperties.db_password(),
            database=AppProperties.db_name()
        )

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
