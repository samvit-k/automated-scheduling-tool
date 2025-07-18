from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_database, save_schedule, get_schedule, user_exists # type: ignore
from models import UserRequest, UserResponse, ScheduleSaveRequest, ScheduleResponse, AIScheduleSaveRequest, AIScheduleResponse # type: ignore
from auth_logic import authenticate_user # type: ignore
from schedule_generation import generate_and_save_schedule # type: ignore

# Create FastAPI application instance
app = FastAPI(
   title="Simple User Authentication API",
   description="A simple backend-only user authentication system using FastAPI and SQLite",
   version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],  # Allow all origins for simplicity
   allow_credentials=True,
   allow_methods=["*"],  # Allow all HTTP methods
   allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
   """
   Initialize the database when the application starts.
   This creates the users table if it doesn't exist.
   """
   print("Initializing database...")
   init_database()
   print("Database initialization complete.")

@app.get("/")
async def root():
   """
   Root endpoint that provides basic API information.
   """
   return {
       "message": "Simple User Authentication API",
       "version": "1.0.0",
       "endpoints": {
           "POST /auth": "Authenticate user (login or register)",
           "POST /schedule/save": "Save or update user schedule",
           "POST /schedule/ai-save": "Save or update AI-generated schedule",
           "POST /schedule/generate": "Generate and save AI schedule from prompt",
           "GET /schedule/{user_id}": "Get user schedule"
       }
   }

@app.post("/auth", response_model=UserResponse)
async def authenticate_user_endpoint(user_request: UserRequest):
   """
   Main authentication endpoint that handles both login and registration.
  
   This endpoint accepts a POST request with username and password.
   It checks if a user with the exact username and password combination exists:
   - If found: Returns success message for login
   - If not found: Creates new user and returns confirmation message
  
   Args:
       user_request (UserRequest): JSON object containing username and password
      
   Returns:
       UserResponse: JSON response with status, message, and optional user details
      
   Example request:
   {
       "username": "john_doe",
       "password": "password123"
   }
  
   Example responses:
   - Login success: {"status": "success", "message": "Login successful", "username": "john_doe", "user_id": 1, "created_at": "2024-01-01T12:00:00"}
   - Registration success: {"status": "success", "message": "User created successfully", "username": "john_doe", "user_id": 1, "created_at": "2024-01-01T12:00:00"}
   - Error: {"status": "error", "message": "Failed to create user. Username may already exist."}
   """
   try:
       # Validate input
       if not user_request.username or not user_request.password:
           raise HTTPException(
               status_code=400,
               detail="Username and password are required"
           )
      
       # Process authentication request
       response = authenticate_user(user_request)
      
       # Return appropriate HTTP status based on response
       if response.status == "success":
           return response
       else:
           raise HTTPException(
               status_code=400,
               detail=response.message
           )
          
   except HTTPException:
       # Re-raise HTTP exceptions
       raise
   except Exception as e:
       # Handle unexpected errors
       print(f"Unexpected error in authentication endpoint: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error"
       )

@app.post("/schedule/save", response_model=ScheduleResponse)
async def save_schedule_endpoint(schedule_request: ScheduleSaveRequest):
   """
   Save or update a schedule for a user.
   
   This endpoint accepts a POST request with user_id and schedule_data.
   It checks if a schedule already exists for the user_id:
   - If exists: Updates the schedule_data and updated_at timestamp
   - If not exists: Creates a new schedule with the provided data
   
   Args:
       schedule_request (ScheduleSaveRequest): JSON object containing user_id and schedule_data
      
   Returns:
       ScheduleResponse: JSON response with status, message, and schedule information
      
   Example request:
   {
       "user_id": 1,
       "schedule_data": {
           "monday": ["9:00 AM - 5:00 PM"],
           "tuesday": ["10:00 AM - 6:00 PM"],
           "wednesday": ["9:00 AM - 5:00 PM"]
       }
   }
   """
   try:
       # Validate input
       if not schedule_request.user_id:
           raise HTTPException(
               status_code=400,
               detail="User ID is required"
           )
       
       if not schedule_request.schedule_data:
           raise HTTPException(
               status_code=400,
               detail="Schedule data is required"
           )
      
       # Save or update schedule
       result = save_schedule(schedule_request.user_id, schedule_request.schedule_data)
      
       # Return appropriate HTTP status based on response
       if result["status"] == "success":
           return ScheduleResponse(**result)
       else:
           raise HTTPException(
               status_code=500,
               detail=result["message"]
           )
          
   except HTTPException:
       # Re-raise HTTP exceptions
       raise
   except Exception as e:
       # Handle unexpected errors
       print(f"Unexpected error in schedule save endpoint: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error"
       )

@app.get("/schedule/{user_id}")
async def get_schedule_endpoint(user_id: int):
   """
   Retrieve a schedule for a user.
   
   This endpoint accepts a GET request with user_id as a path parameter.
   It queries the schedules table for the schedule associated with the user_id.
   
   Args:
       user_id (int): The user ID from the URL path
      
   Returns:
       JSON response with schedule data or error message
      
   Example responses:
   - Success: {"user_id": 1, "schedule_data": {...}, "created_at": "...", "updated_at": "..."}
   - Error: {"error": "No schedule found for this user"}
   """
   try:
       # Validate input
       if not user_id or user_id <= 0:
           raise HTTPException(
               status_code=400,
               detail="Valid user ID is required"
           )
      
       # Get schedule
       schedule = get_schedule(user_id)
      
       if schedule:
           return schedule
       else:
           raise HTTPException(
               status_code=404,
               detail="No schedule found for this user"
           )
          
   except HTTPException:
       # Re-raise HTTP exceptions
       raise
   except Exception as e:
       # Handle unexpected errors
       print(f"Unexpected error in schedule get endpoint: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error"
       )

@app.post("/schedule/ai-save", response_model=AIScheduleResponse)
async def save_ai_schedule_endpoint(schedule_request: AIScheduleSaveRequest):
   """
   Save or update an AI-generated schedule for a user.
   
   This endpoint accepts a POST request with user_id and AI-generated schedule_data.
   It first validates that the user_id exists in the users table, then checks if
   a schedule already exists for that user in the schedules table:
   - If exists: Updates the schedule_data and updated_at timestamp
   - If not exists: Creates a new schedule with the provided data
   
   Args:
       schedule_request (AIScheduleSaveRequest): JSON object containing user_id and AI schedule_data
      
   Returns:
       AIScheduleResponse: JSON response with status, message, and schedule information
      
   Example request:
   {
       "user_id": 1,
       "schedule_data": {
           "monday": [
               {
                   "task_name": "Team Meeting",
                   "start_time": "09:00",
                   "end_time": "10:00",
                   "priority": true,
                   "recurrence": "weekly"
               }
           ],
           "tuesday": [
               {
                   "task_name": "Code Review",
                   "start_time": "14:00",
                   "end_time": "15:00",
                   "priority": false,
                   "recurrence": "daily"
               }
           ]
       }
   }
   """
   try:
       # Validate input
       if not schedule_request.user_id:
           raise HTTPException(
               status_code=400,
               detail="User ID is required"
           )
       
       if not schedule_request.schedule_data:
           raise HTTPException(
               status_code=400,
               detail="Schedule data is required"
           )
      
       # Validate that user exists
       if not user_exists(schedule_request.user_id):
           raise HTTPException(
               status_code=404,
               detail="User not found"
           )
      
       # Convert Pydantic model to dictionary for database storage
       schedule_dict = schedule_request.schedule_data.dict(exclude_none=True)
      
       # Save or update AI schedule using existing save_schedule function
       result = save_schedule(schedule_request.user_id, schedule_dict)
      
       # Return appropriate HTTP status based on response
       if result["status"] == "success":
           # Convert the result back to AIScheduleResponse format
           return AIScheduleResponse(
               status=result["status"],
               message=result["message"],
               user_id=result["user_id"],
               schedule_data=schedule_request.schedule_data,
               created_at=result.get("created_at"),
               updated_at=result.get("updated_at")
           )
       else:
           raise HTTPException(
               status_code=500,
               detail=result["message"]
           )
          
   except HTTPException:
       # Re-raise HTTP exceptions
       raise
   except Exception as e:
       # Handle unexpected errors
       print(f"Unexpected error in AI schedule save endpoint: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error"
       )

@app.post("/schedule/generate")
async def generate_ai_schedule_endpoint(request: dict):
   """
   Generate and save an AI schedule from a user prompt.
   
   This endpoint accepts a POST request with user_id and user_prompt.
   It automatically generates a schedule using the AI, converts it to the proper format,
   and saves it to the database.
   
   Args:
       request: JSON object containing user_id and user_prompt
      
   Returns:
       JSON response with status, message, and schedule information
      
   Example request:
   {
       "user_id": 1,
       "user_prompt": "I have a math test tomorrow, a team meeting on Friday, and need to finish my project by Wednesday"
   }
   """
   try:
       # Validate input
       if not request.get("user_id"):
           raise HTTPException(
               status_code=400,
               detail="User ID is required"
           )
       
       if not request.get("user_prompt"):
           raise HTTPException(
               status_code=400,
               detail="User prompt is required"
           )
      
       user_id = request["user_id"]
       user_prompt = request["user_prompt"]
      
       # Use the complete workflow function
       result = generate_and_save_schedule(user_prompt, user_id)
      
       # Return appropriate HTTP status based on response
       if result["status"] == "success":
           return {
               "status": "success",
               "message": result["message"],
               "user_id": result["user_id"],
               "schedule_data": result["schedule_data"],
               "original_schedule": result.get("original_schedule"),
               "created_at": result.get("created_at"),
               "updated_at": result.get("updated_at")
           }
       else:
           raise HTTPException(
               status_code=500,
               detail=result["message"]
           )
          
   except HTTPException:
       # Re-raise HTTP exceptions
       raise
   except Exception as e:
       # Handle unexpected errors
       print(f"Unexpected error in AI schedule generation endpoint: {e}")
       raise HTTPException(
           status_code=500,
           detail="Internal server error"
       )

@app.get("/health")
async def health_check():
   """
   Health check endpoint to verify the API is running.
   """
   return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
   """
   Run the FastAPI application using uvicorn when this file is executed directly.
   The server will run on http://localhost:8000 by default.
   """
   uvicorn.run(
       "main:app",
       host="0.0.0.0",
       port=8000,
       reload=True,  # Enable auto-reload for development
       log_level="info"
   )