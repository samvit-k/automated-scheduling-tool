# Automated Scheduling Tool

A full-stack application that allows users to generate, save, and manage personalized schedules using AI-generated recommendations. User authentication is handled via a secure login system, and each schedule is tied to a specific user account for persistence and retrieval.

## Features
- User registration and login with username and password
- AI-powered schedule generation from natural language prompts
- Persistent schedule saving and updating linked to user accounts
- JSON-based schedule structure for flexible customization
- RESTful API built with FastAPI
- Planned Google Calendar integration (in progress)

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** SQLite (expandable to PostgreSQL)
- **AI Model:** OpenAI GPT-based schedule generation
- **Frontend:** (To be developed) React or similar SPA framework

## API Endpoints

| Endpoint                 | Method | Description                                |
|------------------------ |--------|--------------------------------------------|
| `/auth`                 | POST   | User login or registration                 |
| `/schedule/save`        | POST   | Save or update manual user schedule        |
| `/schedule/ai-save`     | POST   | Save AI-generated schedule data            |
| `/schedule/generate`    | POST   | Generate and save AI-generated schedule    |
| `/schedule/{user_id}`   | GET    | Retrieve schedule by user ID               |
| `/health`               | GET    | API health check                           |

## Schedule JSON Format Example

```json
{
  "Monday": [
    {
      "task_name": "Math Study",
      "start_time": "09:00 AM",
      "end_time": "10:00 AM",
      "priority": true,
      "recurrence": "Monday, Wednesday, Friday"
    }
  ]
}