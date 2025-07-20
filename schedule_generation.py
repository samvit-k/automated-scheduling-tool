import fitz
import docx
import io
import openai
import json
from pydantic import BaseModel, ValidationError, Field, field_validator, RootModel
import re
from typing import Dict, List, Union, Any
from datetime import datetime, time
import logging
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

UPLOAD_FOLDER = "uploads"
MODEL = "text-embedding-3-small"

openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

model = "gpt-3.5-turbo"

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name="my_collection",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
)

# Get current date and time for the prompt
current_datetime = datetime.now()
current_date_str = current_datetime.strftime("%m/%d/%Y")
current_day = current_datetime.strftime("%A")
current_time_str = current_datetime.strftime("%I:%M %p")

def extract_text_from_file(file_name: str, file_content: bytes):
    """
    Extracts plain text from an in-memory file content based on its extension.
    Supports .txt, .pdf, and .docx files.
    """
    if file_name.endswith(".pdf"):
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text() # type: ignore
            return text
    elif file_name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file_content))
        return "\n".join(para.text for para in doc.paragraphs)
    elif file_name.endswith(".txt"):
        return file_content.decode("utf-8")
    else:
        return None

def process_documents(uploaded_files: List[Dict]) -> List[Dict]:
    docs = []
    for file_info in uploaded_files:
        try:
            filename = file_info['filename']
            file_content = file_info['content']
            text = extract_text_from_file(filename, file_content)
            
            if text:
                docs.append({
                    "filename": filename, 
                    "content": text.strip()
                })
                logger.info(f"Successfully processed {filename}")
            else:
                logger.warning(f"Could not extract text from {filename}")     
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")

    return docs

def generate_chunks(documents_string):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_text(documents_string)

    return [{"id": i, "text": chunk} for i, chunk in enumerate(chunks)]

def generate_single_embedding(client, text_chunk: str):
    response = client.embeddings.create(
        model=MODEL,
        input=text_chunk
    )
    return response.data[0].embedding

def generate_embedding(client, chunks):
    """
    Generates embeddings for a list of text chunks by calling the single embedding function.
    This is used for bulk processing during ingestion.
    """
    embedded_data = []

    for chunk in chunks:
        embedding = generate_single_embedding(client, chunk['text'])
        embedded_data.append({
            "id": chunk['id'],
            "text": chunk['text'],
            "embedding": embedding
        })

    return embedded_data

def embedding_insertion_to_collection(uploaded_files: List[Dict] = None):
    try: 
        collection.delete(where={"id": {"$ne": ""}})
        
        if uploaded_files is None:
            logger.info("No files uploaded to process")
            return
            
        docs = process_documents(uploaded_files)
        documents_string = ''.join(doc['content'] for doc in docs).strip()
        if documents_string:
            chunks = generate_chunks(documents_string)
            collection.add(
                documents=[chunk['text'] for chunk in chunks],
                ids=[str(chunk['id']) for chunk in chunks]
            )
            logger.info(f"Successfully loaded {len(chunks)} document chunks into vector database")
        else:
            logger.info("No documents found to insert into vector database")
    except Exception as e:
        logger.error(f"Error inserting embeddings: {e}")

def collection_similarity_search(query: str, k: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["distances"]
    )
    return results

def generate_schedule_with_context(user_prompt: str, k: int = 5):
    results = collection_similarity_search(user_prompt, k)
    return results

def generate_document_context(user_prompt: str):
    """
    Generate context from uploaded documents based on user prompt similarity.
    Fixed to properly handle ChromaDB query results with error handling.
    """
    try:
        search_results = collection_similarity_search(user_prompt, k=5)
        
        if search_results and 'documents' in search_results and search_results['documents']:
            retrieved_documents = search_results['documents'][0]  # First query result
            distances = search_results['distances'][0] if 'distances' in search_results else []
        else:
            logger.info("No documents found in search results")
            return ""
            
        filtered_documents = []
        for i, doc in enumerate(retrieved_documents):
            if i < len(distances) and distances[i] < 1.0:
                filtered_documents.append(doc)
        
        if filtered_documents:
            context = "\n\n".join(filtered_documents)
            logger.info(f"Retrieved {len(filtered_documents)} relevant document chunks")
            return context
        else:
            logger.info("No relevant documents found for context")
            return ""
    except Exception as e:
        logger.error(f"Error generating document context: {e}")
        return ""

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
   - recurrence: string (use standard values: 'daily', 'weekly', 'monthly', 'none', or specific days like 'Monday', 'Tuesday', etc.)


   CORRECT Example Format:
   {{
   "7/13/2025": [
       {{
       "task_name": "Math Study",
       "start_time": "09:00 AM",
       "end_time": "10:00 AM",
       "priority": true,
       "recurrence": "weekly"
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
   13. RECURRENCE STANDARDS: Use 'daily' for every day tasks, 'weekly' for weekly recurring tasks, 'monthly' for monthly tasks, 'none' for one-time tasks
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
       valid_patterns = ['daily', 'weekly', 'monthly', 'none', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
       if v.lower() not in valid_patterns and not any(day in v for day in valid_patterns[4:]):
           raise ValueError(f'Invalid recurrence pattern: {v}. Must be "daily", "weekly", "monthly", "none", or specific days.')
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
           # Validate date format (MM/DD/YYYY) - more flexible to handle both "7/21/2025" and "07/21/2025"
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
           full_prompt = f"""
            Prompt: {prompt} 
            User Request: {user_prompt}
            Context: {generate_document_context(user_prompt)}
            Please generate a schedule in the exact JSON format specified above.
            """
          
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

def convert_date_schedule_to_weekday_schedule(date_schedule: Dict[str, List[Task]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convert date-based schedule (MM/DD/YYYY) to weekday-based schedule (monday, tuesday, etc.)
    
    Args:
        date_schedule: Dictionary with date keys (MM/DD/YYYY) and task lists as values
        
    Returns:
        Dictionary with weekday keys (monday, tuesday, etc.) and task lists as values
    """
    weekday_schedule = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }
    
    # Map date to weekday with improved date parsing
    for date_str, tasks in date_schedule.items():
        try:
            # Try multiple date formats to handle both "7/21/2025" and "07/21/2025"
            date_obj = None
            date_formats = ["%m/%d/%Y", "%#m/%#d/%Y", "%#m/%d/%Y", "%m/%#d/%Y"]
            
            for date_format in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    break
                except ValueError:
                    continue
            
            if date_obj is None:
                logger.warning(f"Could not parse date {date_str} with any format")
                continue
                
            weekday_name = date_obj.strftime("%A").lower()
            
            if weekday_name in weekday_schedule:
                # Convert Task objects to dictionaries and improve recurrence values
                task_dicts = []
                for task in tasks:
                    task_dict = task.dict()
                    # Improve recurrence values for better consistency
                    recurrence = task_dict.get('recurrence', 'none')
                    if recurrence in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                        # Keep specific days as is
                        pass
                    elif recurrence.lower() in ['daily', 'weekly', 'monthly', 'none']:
                        # Standardize case
                        task_dict['recurrence'] = recurrence.lower()
                    else:
                        # Default to none for unrecognized patterns
                        task_dict['recurrence'] = 'none'
                    task_dicts.append(task_dict)
                
                weekday_schedule[weekday_name] = task_dicts
        except Exception as e:
            logger.warning(f"Error processing date {date_str}: {e}")
            continue
    
    return weekday_schedule

def complete_ai_schedule_workflow(user_prompt: str, user_id: int) -> Dict[str, Any]:
    """
    Complete workflow: prompt → LLM → convert → save to DB
    
    Args:
        user_prompt: The user's scheduling request
        user_id: The user ID to associate the schedule with
        
    Returns:
        Dictionary with status and result information
    """
    try:
        logger.info(f"Starting complete AI schedule workflow for user {user_id}")
        
        # Step 1: Generate schedule with LLM
        logger.info("Generating schedule with LLM...")
        ai_result = generate_schedule(user_prompt)
        
        if isinstance(ai_result, str):
            logger.error(f"LLM generation failed: {ai_result}")
            return {
                "status": "error",
                "message": f"Failed to generate schedule: {ai_result}",
                "user_id": user_id
            }
        
        # Step 2: Convert date-based to weekday-based
        logger.info("Converting date-based schedule to weekday-based...")
        weekday_schedule = convert_date_schedule_to_weekday_schedule(ai_result.root)
        
        # Step 3: Import and use database function
        try:
            from database import save_schedule, user_exists
        except ImportError:
            logger.error("Could not import database functions")
            return {
                "status": "error",
                "message": "Database functions not available",
                "user_id": user_id
            }
        
        # Step 4: Validate user exists
        if not user_exists(user_id):
            logger.error(f"User {user_id} does not exist")
            return {
                "status": "error",
                "message": "User not found",
                "user_id": user_id
            }
        
        # Step 5: Save to database
        logger.info("Saving schedule to database...")
        result = save_schedule(user_id, weekday_schedule)
        
        if result["status"] == "success":
            logger.info("Schedule successfully saved to database")
            return {
                "status": "success",
                "message": "AI schedule generated and saved successfully",
                "user_id": user_id,
                "schedule_data": weekday_schedule,
                "original_schedule": ai_result.root,
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at")
            }
        else:
            logger.error(f"Database save failed: {result['message']}")
            return {
                "status": "error",
                "message": f"Failed to save schedule: {result['message']}",
                "user_id": user_id
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in complete workflow: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "user_id": user_id
        }

def generate_and_save_schedule(user_prompt: str, user_id: int) -> Dict[str, Any]:
    """
    Simplified function for external use - generates and saves schedule in one call
    
    Args:
        user_prompt: The user's scheduling request
        user_id: The user ID to associate the schedule with
        
    Returns:
        Dictionary with status and result information
    """
    return complete_ai_schedule_workflow(user_prompt, user_id)