import sqlite3
from sqlite3 import Error
from database import create_connection
from models import UserRequest, UserResponse, User # type: ignore
from datetime import datetime

def check_user_exists(username: str, password: str) -> tuple[bool, User | None]:
   """
   Check if a user with the given username and password exists in the database.
  
   Args:
       username (str): The username to check
       password (str): The password to check
      
   Returns:
       tuple[bool, User | None]: (exists, user_data)
           - exists: True if user exists with matching credentials, False otherwise
           - user_data: User object if found, None otherwise
   """
   conn = create_connection()
   if conn is None:
       return False, None
  
   try:
       cursor = conn.cursor()
      
       # Query to find user with exact username and password match
       query = "SELECT id, username, password, created_at FROM users WHERE username = ? AND password = ?"
       cursor.execute(query, (username, password))
      
       result = cursor.fetchone()
      
       if result and result[0] is not None:
           # User found with matching credentials
           user = User(
               id=result[0],
               username=result[1],
               password=result[2],
               created_at=datetime.fromisoformat(result[3])
           )
           return True, user
       else:
           # No user found with matching credentials
           return False, None
          
   except Error as e:
       print(f"Error checking user existence: {e}")
       return False, None
   finally:
       conn.close()

def create_new_user(username: str, password: str) -> tuple[bool, User | None]:
   """
   Create a new user in the database with the provided username and password.
  
   Args:
       username (str): The username for the new user
       password (str): The password for the new user
      
   Returns:
       tuple[bool, User | None]: (success, user_data)
           - success: True if user created successfully, False otherwise
           - user_data: User object if created, None otherwise
   """
   conn = create_connection()
   if conn is None:
       return False, None
  
   try:
       cursor = conn.cursor()
      
       # Check if username already exists (for uniqueness constraint)
       check_query = "SELECT id FROM users WHERE username = ?"
       cursor.execute(check_query, (username,))
      
       if cursor.fetchone():
           # Username already exists
           return False, None
      
       # Insert new user with plain text username and password
       insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
       cursor.execute(insert_query, (username, password))
      
       # Get the created user data
       user_id = cursor.lastrowid
       if user_id is None:
           return False, None
          
       created_at = datetime.now()
      
       user = User(
           id=user_id,
           username=username,
           password=password,
           created_at=created_at
       )
      
       conn.commit()
       return True, user
      
   except Error as e:
       print(f"Error creating new user: {e}")
       conn.rollback()
       return False, None
   finally:
       conn.close()

def authenticate_user(user_request: UserRequest) -> UserResponse:
   """
   Main authentication function that handles both login and registration.
  
   Logic:
   1. Check if user exists with exact username and password match
   2. If found: Return success message for login
   3. If not found: Create new user and return confirmation message
  
   Args:
       user_request (UserRequest): The user authentication request
      
   Returns:
       UserResponse: Response with status and message
   """
   username = user_request.username
   password = user_request.password
  
   # Check if user exists with matching credentials
   user_exists, existing_user = check_user_exists(username, password)
  
   if user_exists and existing_user is not None:
       # User found - successful login
       return UserResponse(
           status="success",
           message="Login successful",
           username=existing_user.username,
           user_id=existing_user.id,
           created_at=existing_user.created_at
       )
   else:
       # User not found - create new user
       user_created, new_user = create_new_user(username, password)
      
       if user_created and new_user is not None:
           return UserResponse(
               status="success",
               message="User created successfully",
               username=new_user.username,
               user_id=new_user.id,
               created_at=new_user.created_at
           )
       else:
           # Failed to create user (likely username already exists)
           return UserResponse(
               status="error",
               message="Failed to create user. Username may already exist."
           )