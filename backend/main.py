import json
import pandas as pd
from enum import Enum

from fastapi import FastAPI, Query, HTTPException, Request 
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware 

from io import StringIO

# --- 1. Application Setup & Data Loading ---

# --- 2. ADD THIS MIDDLEWARE ---
origins = [
    "http://localhost:3000", # The origin for our React app
]



app = FastAPI(
    title="Virtuagym Export Service",
    description="A service to export gym reports in different formats.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

DATA_DIR = "./data/"

# A simple function to load our JSON data into Pandas DataFrames
def load_data():
    try:
        data = {
            "clubs": pd.read_json(f"{DATA_DIR}clubs.json"),
            "members": pd.read_json(f"{DATA_DIR}members.json"),
            "checkins": pd.read_json(f"{DATA_DIR}checkins.json"),
            "exercises": pd.read_json(f"{DATA_DIR}exercises.json"),
            "instances": pd.read_json(f"{DATA_DIR}exercise_instances.json")
        }
        
        # Convert timestamp columns to actual datetime objects for filtering
        data["checkins"]["timestamp"] = pd.to_datetime(data["checkins"]["timestamp"])
        data["instances"]["timestamp"] = pd.to_datetime(data["instances"]["timestamp"])
        
        print("All data loaded successfully into Pandas DataFrames.")
        return data
    except FileNotFoundError as e:
        print(f"ERROR: Missing data file {e.filename}. Please run the scripts first.")
        return None
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return None

# Load data on startup
db = load_data()
if db is None:
    exit()

# --- 2. Helper Enums & Functions ---

# Define allowed report types and formats using Enums
# This provides automatic validation in the API endpoint
class ReportType(str, Enum):
    activity = "activity"
    popular_exercises = "popular-exercises"

class ReportFormat(str, Enum):
    json = "json"
    csv = "csv"

# Function to convert a DataFrame to a CSV string and create a streaming response
def create_csv_response(df: pd.DataFrame, filename: str):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(csv_buffer, media_type="text/csv", headers=headers)

# --- 3. API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Virtuagym Export Service!"}


# --- CHANGE 2: Modify the get_exercises function ---
@app.get("/api/exercises")
def get_exercises(request: Request, offset: int = 0, limit: int = 20):
    """
    Returns a paginated list of the locally stored exercises, 
    including next and previous page links.
    """
    total_exercises = len(db["exercises"])
    paginated_exercises = db["exercises"].iloc[offset : offset + limit]
    
    # --- Logic to build next and previous URLs ---
    next_url = None
    if offset + limit < total_exercises:
        next_offset = offset + limit
        # request.url.path gives us '/api/exercises'
        next_url = f"{request.base_url}{request.url.path.lstrip('/')}?offset={next_offset}&limit={limit}"

    previous_url = None
    if offset > 0:
        # Ensure previous offset doesn't go below 0
        previous_offset = max(0, offset - limit)
        previous_url = f"{request.base_url}{request.url.path.lstrip('/')}?offset={previous_offset}&limit={limit}"
    # --- End of URL logic ---

    response_data = {
        "count": total_exercises, # Renamed 'total' to 'count' (common convention)
        "next": next_url,
        "previous": previous_url,
        "results": paginated_exercises.to_dict("records") # Renamed 'data' to 'results'
    }
    
    return JSONResponse(content=response_data)


@app.get("/api/export")
def get_export(
    type: ReportType,
    format: ReportFormat
):
    """
    Generates and returns a dataset based on the report type and format.
    """
    if type == ReportType.activity:
        # --- Logic for Member Activity Report ---
        
        # 1. Join Checkins with Clubs
        df = pd.merge(
            db["checkins"],
            db["clubs"],
            on="club_id",
            how="left"
        )
        
        # 2. Extract month-year (e.g., "2025-10")
        df["month_year"] = df["timestamp"].dt.to_period("M").astype(str)
        
        # 3. Group by club and month, then count check-ins
        report = df.groupby(
            ["club_id", "club_name", "month_year"]
        ).size().reset_index(name="total_checkins")
        
        filename = "member_activity.csv"

    elif type == ReportType.popular_exercises:
        # --- Logic for Most Popular Exercises Report ---
        
        exercise_names = db["exercises"][["exercise_id", "name"]]

        # 1. Join Instances with Exercises and Clubs
        df = pd.merge(
            db["instances"],
            exercise_names,
            on="exercise_id",
            how="left"
        )
        print('okay before merges')
        print(df.head(5))
        df = pd.merge(
            df,
            db["clubs"],
            on="club_id",
            how="left"
        )
        print('okay after merges') 
        # 2. Group by club and exercise, then count usage
        usage_counts = df.groupby(
            ["club_id", "club_name", "exercise_id", "name"]
        ).size().reset_index(name="usage_count")
        
        # 3. For each club, get the top 10
        report = usage_counts.sort_values(
            by=["club_id", "usage_count"], ascending=[True, False]
        ).groupby("club_id").head(10).reset_index(drop=True)
        
        filename = "popular_exercises.csv"

    else:
        # This case is technically handled by the Enum, but it's good practice
        raise HTTPException(status_code=400, detail="Invalid report type.")

    # --- 4. Return in the requested format ---
    if format == ReportFormat.json:
        # Convert the final report DataFrame to a JSON list
        return JSONResponse(content=report.to_dict("records"))
    
    elif format == ReportFormat.csv:
        # Return the CSV response
        return create_csv_response(report, filename)