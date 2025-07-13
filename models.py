from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserRequest(BaseModel):
   """
   Pydantic model for user authentication requests.
   Contains username and password fields for login/registration.
   """
   username: str
   password: str

class UserResponse(BaseModel):
   """
   Pydantic model for user authentication responses.
   Contains status message and optional user information.
   """
   status: str
   message: str
   username: Optional[str] = None
   user_id: Optional[int] = None
   created_at: Optional[datetime] = None

class User(BaseModel):
   """
   Pydantic model representing a user in the database.
   Used for internal data handling and response formatting.
   """
   id: int
   username: str
   password: str
   created_at: datetime