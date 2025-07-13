import sqlite3
from sqlite3 import Error
import os

# Database configuration
DATABASE_FILE = "users.db"

def create_connection():
   """
   Create a database connection to SQLite database.
   Returns a connection object or None if connection fails.
   """
   try:
       # Create connection to SQLite database
       conn = sqlite3.connect(DATABASE_FILE)
       return conn
   except Error as e:
       print(f"Error connecting to database: {e}")
       return None

def create_users_table():
   """
   Create the users table if it doesn't exist.
   The table stores username and password as plain text as requested.
   """
   conn = create_connection()
   if conn is not None:
       try:
           cursor = conn.cursor()
          
           # Create users table with username and password columns
           # Both fields are TEXT to store the plain text values
           create_table_sql = """
           CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL UNIQUE,
               password TEXT NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           );
           """
          
           cursor.execute(create_table_sql)
           conn.commit()
           print("Users table created successfully or already exists.")
          
       except Error as e:
           print(f"Error creating table: {e}")
       finally:
           conn.close()
   else:
       print("Error: Could not create database connection.")

def init_database():
   """
   Initialize the database by creating the users table.
   This function should be called when the application starts.
   """
   create_users_table()