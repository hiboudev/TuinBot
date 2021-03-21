import mysql.connector


# Doc mysql python : https://python.doctor/page-database-data-base-donnees-query-sql-mysql-postgre-sqlite
class DatabaseConnection:

    def __enter__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tuinbot"
        )

        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
