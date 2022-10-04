import mysql
import mysql.connector
DB = {
            "user": "church",
            "password": "Church99",
            "host": "localhost",
            "database": "ChurchDB",
        }

DBConnection = mysql.connector.connect(**DB)
cursor = DBConnection.cursor()
sql = "UPDATE tblSermon SET Outline = 'C:\\\\Users\\\\jonat\\\\Documents\\\\PythonProjects\\\\ChurchManager\\\\Outlines' WHERE ID = 9;"
cursor.execute(sql)
DBConnection.commit()
cursor.close()