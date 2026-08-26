"""Initialize the database-limited local test account during recovery mode."""

import mariadb

from credential_store import read_credential


TARGET = "ChurchManager/LocalTestAdmin"


def main():
    username, password = read_credential(TARGET)
    if username != "church":
        raise RuntimeError("Expected the stored local test username to be church")
    connection = mariadb.connect(
        host="127.0.0.1", port=3306, user="root", autocommit=True
    )
    try:
        cursor = connection.cursor()
        cursor.execute("FLUSH PRIVILEGES")
        cursor.execute(
            "CREATE USER IF NOT EXISTS 'church'@'127.0.0.1' IDENTIFIED BY ?",
            (password,),
        )
        cursor.execute(
            "ALTER USER 'church'@'127.0.0.1' IDENTIFIED BY ?", (password,)
        )
        cursor.execute(
            "GRANT ALL PRIVILEGES ON ChurchDBTest.* "
            "TO 'church'@'127.0.0.1'"
        )
        cursor.execute(
            "GRANT ALL PRIVILEGES ON JSFormTest.* "
            "TO 'church'@'127.0.0.1'"
        )
        cursor.execute("FLUSH PRIVILEGES")
    finally:
        password = ""
        connection.close()
    print("Local test account created with database-limited privileges.")


if __name__ == "__main__":
    main()
