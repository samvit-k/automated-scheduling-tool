from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import init_database # type: ignore
from models import UserRequest, UserResponse # type: ignore
from auth_logic import authenticate_user # type: ignore


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
           "POST /auth": "Authenticate user (login or register)"
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