import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mike@4449",
        database="civitrack_db"
    )
