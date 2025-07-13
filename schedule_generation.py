import openai
import json
from pydantic import BaseModel, ValidationError, Field, field_validator, RootModel
import re
from typing import Dict, List, Union
from datetime import datetime, time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

model = "gpt-3.5-turbo"

# Get current date and time for the prompt
current_datetime = datetime.now()
current_date_str = current_datetime.strftime("%m/%d/%Y")
current_day = current_datetime.strftime("%A")
current_time_str = current_datetime.strftime("%I:%M %p")

prompt = f"""
   You are an expert AI assistant specializing in generating personalized, structured daily schedules based on a user's goals, preferences, and contextual data. The user provides a scheduling prompt describing their needs, including classwork, extracurricular activities, personal tasks, and other commitments.
   The user may also upload supporting documents such as existing schedules or notes, and specify whether their request applies to a repeating schedule (e.g., every day) or to specific days of the week, using button-based inputs. Your task is to create a clear, realistic, and organized schedule that maximizes productivity while ensuring all tasks are addressed.
   Prioritize tasks identified as high priority, either explicitly marked by the user or clearly indicated through context. If the priority level of a task is unclear, do not assume; instead, prompt the user for confirmation before proceeding. Ensure high-priority tasks are scheduled first with sufficient focus time while respecting unmovable tasks (such as fixed classes or appointments).
   Construct the schedule with no overlapping tasks, appropriate breaks between sessions, and time slots that align with typical daily routines. If a task or request cannot be fully accommodated based on the user's constraints, provide a brief, clear explanation in plain text and suggest that the user refine their input for greater specificity.
  
   CRITICAL: You MUST return the schedule in the following EXACT JSON format. The date keys MUST be in MM/DD/YYYY format (e.g., "7/13/2025", "12/25/2024"), NOT day names like "Monday" or "Tuesday". Convert any day references to actual dates.
  
   CURRENT DATE AND TIME CONTEXT:
   - Today's date: {current_date_str} ({current_day})
   - Current time: {current_time_str}
   - Use this as your reference point for all date calculations
  
   DATE AND TIME AWARENESS:
   - Use the current date ({current_date_str}) as your reference point for scheduling
   - Interpret user's natural language for time references with context awareness
   - Consider urgency indicators: "by tomorrow", "urgent", "asap", "due soon" = high priority
   - Understand implied timelines: "when possible", "sometime this week", "when I have time" = flexible
   - Convert relative references to actual dates based on context and urgency
   - "tomorrow" typically means next day, but consider if user means "by tomorrow" (urgent) vs "for tomorrow" (planned)
   - "next [day]" = next occurrence of that day from current date
   - "this [day]" = this week's occurrence of that day
   - "next week" = 7+ days from current date
   - Consider user's implied timeline and urgency from context clues
   - Use realistic, current dates that make sense for the user's timeline
   - All dates should be in the current year or near future, not past dates
  
   Each task object should contain:
   - task_name: string
   - start_time: string (formatted as "HH:MM AM/PM")
   - end_time: string (formatted as "HH:MM AM/PM")
   - priority: boolean (true if marked high-priority)
   - recurrence: string (e.g., 'daily', 'none', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')


   CORRECT Example Format:
   {{
   "7/13/2025": [
       {{
       "task_name": "Math Study",
       "start_time": "09:00 AM",
       "end_time": "10:00 AM",
       "priority": true,
       "recurrence": "Monday, Wednesday, Friday"
       }},
       {{
       "task_name": "Physics Review",
       "start_time": "10:15 AM",
       "end_time": "11:00 AM",
       "priority": false,
       "recurrence": "daily"
       }}
   ],
   "7/14/2025": [
       {{
       "task_name": "English Essay",
       "start_time": "02:00 PM",
       "end_time": "04:00 PM",
       "priority": true,
       "recurrence": "none"
       }}
   ]
   }}


   INCORRECT Example (DO NOT USE):
   {{
   "Monday": [...],  // WRONG - use "7/13/2025" instead
   "Tuesday": [...],  // WRONG - use "7/14/2025" instead
   "Friday": [...]    // WRONG - use "7/17/2025" instead
   }}

   IMPORTANT RULES:
   1. Date keys MUST be in MM/DD/YYYY format (e.g., "7/13/2025", "12/25/2024")
   2. NEVER use day names like "Monday", "Tuesday", "Friday" as date keys
   3. Convert any day references in the user's request to actual dates based on current date ({current_date_str})
   4. Use realistic dates that make sense for the current time period
   5. Maintain clarity, balance, and logical task distribution
   6. Make reasonable assumptions if any user input is ambiguous
   7. Clearly note any assumptions or required clarifications in a short text response alongside the JSON output
   8. Always use current date ({current_date_str}) as reference point for relative date calculations
   9. Do NOT use dates from the past - only use current date or future dates
   10. PRIORITY SCHEDULING: When user says "by [timeframe]", schedule that task for the earliest possible time within that constraint
   11. TASK CONSOLIDATION: Don't split single tasks across multiple days unless explicitly requested or necessary
   12. URGENCY INTERPRETATION: "urgent", "asap", "due soon", "by [date]" = high priority and immediate scheduling
"""

class Task(BaseModel):
   """
   Pydantic model for individual task validation.
   Ensures each task follows the exact format specified in the prompt.
   """

   task_name: str = Field(..., description="Name of the task")
   start_time: str = Field(..., description="Start time of the task")
   end_time: str = Field(..., description="End time of the task")
   priority: bool = Field(..., description="Priority of the task")
   recurrence: str = Field(..., description="Recurrence of the task")

   @field_validator('start_time', 'end_time')
   def valid_time_format(cls, v):
       """Validate time format matches HH:MM AM/PM pattern."""
       time_pattern = r'^(0?[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$'
       if not re.match(time_pattern, v):
           raise ValueError('Invalid time format. Must be in HH:MM AM/PM format.')
       return v

   @field_validator('task_name')
   def valid_task_name(cls, v):
       """Validate task name is not empty."""
       if not v.strip():
           raise ValueError('Task name cannot be empty or whitespace only.')
       return v.strip()
  
   @field_validator('recurrence')
   def valid_recurrence(cls, v):
       """Validate recurrence pattern."""
       valid_patterns = ['daily', 'none', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
       if v.lower() not in valid_patterns and not any(day in v for day in valid_patterns[2:]):
           raise ValueError(f'Invalid recurrence pattern: {v}. Must be "daily", "none", or specific days.')
       return v
  
   @field_validator('priority')
   def valid_priority(cls, v):
       """Validate priority is a boolean."""
       if not isinstance(v, bool):
           raise ValueError('Priority must be a boolean.')
       return v

   @field_validator('end_time')
   def validate_end_after_start(cls, v, info):
       """Validate that end time is after start time."""
       start_time = info.data.get('start_time')
       if start_time:
           try:
               start_time_obj = datetime.strptime(start_time, "%I:%M %p").time()
               end_time_obj = datetime.strptime(v, "%I:%M %p").time()
               if end_time_obj <= start_time_obj:
                   raise ValueError('End time must be after start time.')
           except ValueError:
               # If time parsing fails, let the time_format validator handle it
               pass
       return v

class Schedule(RootModel[Dict[str, List[Task]]]):
   """
   Pydantic root model for the complete schedule validation.
   Ensures the entire schedule follows the exact format specified in the prompt.
   """
   @field_validator('root')
   @classmethod
   def validate_schedule_structure(cls, v):
       if not v:
           raise ValueError('Schedule cannot be empty')
       for date_key, tasks in v.items():
           # Validate date format (MM/DD/YYYY)
           date_pattern = r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{4}$'
           if not re.match(date_pattern, date_key):
               raise ValueError(f'Invalid date format: {date_key}. Must be MM/DD/YYYY')
           # Validate tasks list
           if not isinstance(tasks, list):
               raise ValueError(f'Tasks for {date_key} must be a list')
           if not tasks:
               raise ValueError(f'No tasks found for date: {date_key}')
       return v

class ScheduleValidator:
   """
   Comprehensive validation system for LLM schedule output.
   Ensures the output matches the exact format specified in the prompt.
   """

   def __init__(self):
       self.max_retries = 3
       self.validation_errors = []
  
   def validate_time_sequence(self, tasks: List[Task]) -> List[str]:
       """
       Validate that tasks don't overlap and are in chronological order.
       """
       errors = []
       sorted_tasks = sorted(tasks, key=lambda x: self._parse_time(x.start_time))
      
       for i in range(len(sorted_tasks) - 1):
           current_end = self._parse_time(sorted_tasks[i].end_time)
           next_start = self._parse_time(sorted_tasks[i + 1].start_time)
          
           if current_end >= next_start:
               errors.append(f"Task overlap detected: '{sorted_tasks[i].task_name}' ends at {sorted_tasks[i].end_time} "
                           f"and '{sorted_tasks[i + 1].task_name}' starts at {sorted_tasks[i + 1].start_time}")
       return errors
  
   def _parse_time(self, time_str: str) -> time:
       """Parse time string to time object for comparison."""
       try:
           return datetime.strptime(time_str, "%I:%M %p").time()
       except ValueError:
           raise ValueError(f"Invalid time format: {time_str}")
  
   def validate_structure_json(self, json_str: str) -> Dict:
       """
       Validate that the JSON string matches the expected structure.
       """
       try:
           data = json.loads(json_str)
       except json.JSONDecodeError as e:
           raise ValueError(f"Invalid JSON format: {e}")
      
       # Check if it's a dictionary
       if not isinstance(data, dict):
           raise ValueError("Schedule must be a JSON object")
      
       # Check if it has the expected structure
       if not data:
           raise ValueError("Schedule cannot be empty")
      
       return data

   def validate_schedule(self, json_str: str) -> Union[Schedule, List[str]]:
       """
       Comprehensive validation of the LLM output.
       Returns validated Schedule object or list of validation errors.
       """
       errors = []
      
       try:
           # Step 1: Validate JSON structure
           data = self.validate_structure_json(json_str)
          
           # Step 2: Validate with Pydantic models
           schedule = Schedule(root=data)
          
           # Step 3: Validate time sequences for each day
           for date_key, tasks in schedule.root.items():
               time_errors = self.validate_time_sequence(tasks)
               errors.extend(time_errors)
          
           if errors:
               return errors
          
           return schedule
          
       except ValidationError as e:
           errors.append(f"Validation error: {e}")
           return errors
       except Exception as e:
           errors.append(f"Unexpected error: {e}")
           return errors
  
   def format_validation_errors(self, errors: List[str]) -> str:
       """
       Format validation errors into a clear message for the LLM.
       """
       if not errors:
           return "Validation passed"
      
       error_msg = "The schedule format is incorrect. Please fix the following issues:\n"
       for i, error in enumerate(errors, 1):
           error_msg += f"{i}. {error}\n"
      
       error_msg += "\nPlease ensure the output follows the exact format specified in the prompt."
       return error_msg

def generate_schedule(user_prompt: str, max_retries: int = 3) -> Union[Schedule, str]:
   """
   Generate schedule with comprehensive validation and retry logic.
  
   Args:
       user_prompt: The user's scheduling request
       max_retries: Maximum number of retry attempts if validation fails
  
   Returns:
       Validated Schedule object or error message string
   """
   validator = ScheduleValidator()
  
   for attempt in range(max_retries):
       try:
           logger.info(f"Generating schedule (attempt {attempt + 1}/{max_retries})")
          
           # Create the full prompt with user input
           full_prompt = f"{prompt}\n\nUser Request: {user_prompt}\n\nPlease generate a schedule in the exact JSON format specified above."
          
           response = openai.chat.completions.create(
               model=model,
               messages=[{"role": "user", "content": full_prompt}],
               response_format={"type": "json_object"},
               temperature=0.7  # Slightly higher for creativity while maintaining structure
           )
          
           llm_output = response.choices[0].message.content
           if llm_output is None:
               raise ValueError("LLM returned empty response")

           logger.info("Received LLM response, validating...")
          
           # Validate the output
           validation_result = validator.validate_schedule(llm_output)
          
           if isinstance(validation_result, Schedule):
               logger.info("Schedule validation successful")
               return validation_result
           else:
               # Validation failed, prepare retry with error feedback
               error_message = validator.format_validation_errors(validation_result)
               logger.warning(f"Validation failed (attempt {attempt + 1}): {error_message}")
              
               if attempt < max_retries - 1:
                   # Add error feedback to the prompt for retry
                   retry_prompt = f"{prompt}\n\nUser Request: {user_prompt}\n\nPrevious attempt failed validation. Please fix these issues:\n{error_message}\n\nGenerate a corrected schedule in the exact JSON format specified."
                  
                   response = openai.chat.completions.create(
                       model=model,
                       messages=[{"role": "user", "content": retry_prompt}],
                       response_format={"type": "json_object"},
                       temperature=0.5  # Lower temperature for more precise formatting
                   )
                  
                   llm_output = response.choices[0].message.content
                   if llm_output is None:
                       raise ValueError("LLM returned empty response")
                  
                   validation_result = validator.validate_schedule(llm_output)
                  
                   if isinstance(validation_result, Schedule):
                       logger.info("Schedule validation successful on retry")
                       return validation_result
               else:
                   return f"Failed to generate valid schedule after {max_retries} attempts. Last error: {error_message}"
      
       except Exception as e:
           logger.error(f"Error during schedule generation (attempt {attempt + 1}): {e}")
           if attempt == max_retries - 1:
               return f"Error generating schedule: {str(e)}"
  
   return "Failed to generate schedule after maximum retry attempts"

if __name__ == "__main__":
   user_prompt = "I have a lot of homework to do. I need to finish it by tomorrow. I have a test on Friday. I have a soccer game on Saturday. I have a doctor's appointment on Sunday. I have a job interview on Monday. I have a dentist appointment on Tuesday. I have a dentist appointment on Wednesday. I have a dentist appointment on Thursday. I have a dentist appointment on Friday. I have a dentist appointment on Saturday. I have a dentist appointment on Sunday."
   schedule = generate_schedule(user_prompt)
   print(schedule)