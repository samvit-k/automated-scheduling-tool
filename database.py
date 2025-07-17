import sqlite3
from sqlite3 import Error
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

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

def create_schedules_table():
   """
   Create the schedules table if it doesn't exist.
   The table stores scheduling data with foreign key relationship to users.
   """
   conn = create_connection()
   if conn is not None:
       try:
           cursor = conn.cursor()
          
           # Create schedules table with the specified schema
           create_table_sql = """
           CREATE TABLE IF NOT EXISTS schedules (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER NOT NULL,
               schedule_data TEXT NOT NULL,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (user_id) REFERENCES users (id)
           );
           """
          
           cursor.execute(create_table_sql)
           conn.commit()
           print("Schedules table created successfully or already exists.")
          
       except Error as e:
           print(f"Error creating schedules table: {e}")
       finally:
           conn.close()
   else:
       print("Error: Could not create database connection.")

def save_schedule(user_id: int, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
   """
   Save or update a schedule for a user.
   
   Args:
       user_id (int): The user ID
       schedule_data (Dict[str, Any]): The schedule data as a dictionary
   
   Returns:
       Dict[str, Any]: Response with status and schedule information
   """
   conn = create_connection()
   if conn is not None:
       try:
           cursor = conn.cursor()
           
           # Check if schedule already exists for this user
           check_sql = "SELECT id, created_at FROM schedules WHERE user_id = ?"
           cursor.execute(check_sql, (user_id,))
           existing_schedule = cursor.fetchone()
           
           # Convert schedule_data to JSON string
           schedule_json = json.dumps(schedule_data)
           
           if existing_schedule:
               # Update existing schedule
               update_sql = """
               UPDATE schedules 
               SET schedule_data = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE user_id = ?
               """
               cursor.execute(update_sql, (schedule_json, user_id))
               conn.commit()
               
               return {
                   "status": "success",
                   "message": "Schedule updated successfully",
                   "user_id": user_id,
                   "schedule_data": schedule_data,
                   "created_at": existing_schedule[1],
                   "updated_at": datetime.now().isoformat()
               }
           else:
               # Insert new schedule
               insert_sql = """
               INSERT INTO schedules (user_id, schedule_data, created_at, updated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
               """
               cursor.execute(insert_sql, (user_id, schedule_json))
               conn.commit()
               
               # Get the created schedule details
               cursor.execute("SELECT created_at FROM schedules WHERE user_id = ?", (user_id,))
               created_at = cursor.fetchone()[0]
               
               return {
                   "status": "success",
                   "message": "Schedule created successfully",
                   "user_id": user_id,
                   "schedule_data": schedule_data,
                   "created_at": created_at,
                   "updated_at": created_at
               }
               
       except Error as e:
           print(f"Error saving schedule: {e}")
           return {
               "status": "error",
               "message": f"Failed to save schedule: {e}"
           }
       finally:
           conn.close()
   else:
       return {
           "status": "error",
           "message": "Could not create database connection"
       }

def get_schedule(user_id: int) -> Optional[Dict[str, Any]]:
   """
   Retrieve a schedule for a user.
   
   Args:
       user_id (int): The user ID
   
   Returns:
       Optional[Dict[str, Any]]: Schedule data if found, None otherwise
   """
   conn = create_connection()
   if conn is not None:
       try:
           cursor = conn.cursor()
           
           # Query for schedule
           select_sql = """
           SELECT schedule_data, created_at, updated_at 
           FROM schedules 
           WHERE user_id = ?
           """
           cursor.execute(select_sql, (user_id,))
           result = cursor.fetchone()
           
           if result:
               schedule_data = json.loads(result[0])
               return {
                   "user_id": user_id,
                   "schedule_data": schedule_data,
                   "created_at": result[1],
                   "updated_at": result[2]
               }
           else:
               return None
               
       except Error as e:
           print(f"Error retrieving schedule: {e}")
           return None
       finally:
           conn.close()
   else:
       return None

def init_database():
   """
   Initialize the database by creating the users and schedules tables.
   This function should be called when the application starts.
   """
   create_users_table()
   create_schedules_table()