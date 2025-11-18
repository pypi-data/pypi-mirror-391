import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from .. import properties

class Database:
    @staticmethod
    def connect():
        try:
            conn = mysql.connector.connect(
                host=properties.DATABASE_HOST,
                user=properties.DATABASE_USER,
                password=properties.DATABASE_PASSWORD
            )
            print(f"[DB] Connected with user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            return conn
        except Error as e:
            print(f"[DB] ERROR: Couldn't connect to user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            return None
        
    @staticmethod
    @contextmanager
    def session():
        conn = Database.connect()
        if not conn or not conn.is_connected():
            raise ConnectionError("[DB] Couldn't create session")
        
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("[DB] Couldn't yield conn")
        finally:
            cursor.close()
            conn.close()
