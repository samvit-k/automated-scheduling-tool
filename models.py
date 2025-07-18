from pydantic import BaseModel
from typing import Optional, Dict, Any
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

class ScheduleSaveRequest(BaseModel):
   """
   Pydantic model for schedule save requests.
   Contains user_id and schedule_data for saving/updating schedules.
   """
   user_id: int
   schedule_data: Dict[str, Any]

class ScheduleResponse(BaseModel):
   """
   Pydantic model for schedule responses.
   Contains status, message, and optional schedule information.
   """
   status: str
   message: str
   user_id: Optional[int] = None
   schedule_data: Optional[Dict[str, Any]] = None
   created_at: Optional[datetime] = None
   updated_at: Optional[datetime] = None

class Task(BaseModel):
   """
   Pydantic model for individual tasks in the AI-generated schedule.
   Each task has a name, start/end times, priority flag, and recurrence pattern.
   """
   task_name: str
   start_time: str
   end_time: str
   priority: bool
   recurrence: str

class AIScheduleData(BaseModel):
   """
   Pydantic model for AI-generated schedule data.
   Contains schedules for each weekday with lists of tasks.
   """
   monday: Optional[list[Task]] = None
   tuesday: Optional[list[Task]] = None
   wednesday: Optional[list[Task]] = None
   thursday: Optional[list[Task]] = None
   friday: Optional[list[Task]] = None
   saturday: Optional[list[Task]] = None
   sunday: Optional[list[Task]] = None

class AIScheduleSaveRequest(BaseModel):
   """
   Pydantic model for AI schedule save requests.
   Contains user_id and AI-generated schedule_data.
   """
   user_id: int
   schedule_data: AIScheduleData

class AIScheduleResponse(BaseModel):
   """
   Pydantic model for AI schedule responses.
   Contains status, message, and schedule information with timestamps.
   """
   status: str
   message: str
   user_id: int
   schedule_data: AIScheduleData
   created_at: Optional[datetime] = None
   updated_at: Optional[datetime] = None