"""
Tool helps to convert absolute URLs into relative URLs.
"""

import os

import MySQLdb


class Database:
    """
    Class helps to convert absolute URLs into relative URLs.
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        self.__db_params = {
            "host": host,
            "user": user,
            "passwd": password,
            "db": database,
        }

    def __connect(self):
        """
        Establish a database connection.
        """
        try:
            connection = MySQLdb.connect(**self.__db_params)
            return connection
        except MySQLdb.Error as error:
            print(f"Failed to connect to the database: {error}")
            return None

    @staticmethod
    def db_connection(func):
        """
        Static method wrapper as a db connector.
        """

        def wrapper(self, *args, **kwargs):
            connection = self.__connect()
            if connection:
                try:
                    cursor = connection.cursor()
                    result = func(self, cursor, *args, **kwargs)
                    connection.commit()
                    return result
                except MySQLdb.Error as e:
                    print(f"Error: '{e}'")
                finally:
                    cursor.close()
                    connection.close()
            else:
                print("Failed to connect to database")

        return wrapper

    @db_connection
    def execute_query(self, cursor, query, params=None):
        cursor.execute(query, params)
        return cursor.fetchall()


def update_table(db: Database, table: str, field: str, orig: str, modif: str):
    ID = 0
    CONTENT = 1

    query = f"SELECT id, {field} FROM {table};"
    results = db.execute_query(query)
    for row in results:
        content = row[CONTENT].replace(orig, modif)
        query = f"UPDATE {table} SET {field} = %s WHERE id = %s"
        db.execute_query(query, (content, row[ID]))


if __name__ == "__main__":
    db = Database(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("MYSQL_DATABASE", "lumieres_lausanne"),
        user=os.getenv("MYSQL_USER", "lluser-dev"),
        password=os.getenv("MYSQL_PASSWORD", "lluser-password"),
    )
    tables = ["fiches_freecontent", "fiches_news"]
    for table in tables:
        update_table(db, table, "content", 'href="https://lumieres.unil.ch', 'href="')
    update_table(db, "fiches_project", "description", 'href="https://lumieres.unil.ch', 'href="')
    update_table(db, "fiches_image", "link", "https://lumieres.unil.ch", "")
