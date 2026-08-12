"""Remove only the incomplete local test schema created by a failed restore."""

import mariadb

from credential_store import read_credential


def main():
    username, password = read_credential("ChurchManager/LocalTestAdmin")
    connection = mariadb.connect(
        host="127.0.0.1", port=3306, user=username, password=password,
        autocommit=True,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS ChurchDBTest")
        # JSFormTest was not reached, but remove it if the failed run created it.
        cursor.execute("DROP DATABASE IF EXISTS JSFormTest")
    finally:
        password = ""
        connection.close()
    print("Removed only the incomplete local ChurchDBTest/JSFormTest schemas.")


if __name__ == "__main__":
    main()
