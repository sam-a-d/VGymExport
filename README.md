# Virtuagym Export Service

This is a full-stack application, built with **FastAPI**, **Pandas**, and **React**, that allows a gym manager to preview and export data reports in both CSV and JSON formats.

This project was built as part of the Virtuagym Software Engineering Internship Challenge. It fulfills the core requirement of building an export service and an optional frontend to visualize the data.

## Features

* **RESTful Backend API**: A clean, paginated API (HATEOAS standard) for accessing exercise data, built with FastAPI.
* **Rich Frontend UI**: A React application to visualize and download reports.
    * **Dynamic Table Visualization**: Previews reports in a clean, sortable table.
    * **Stacked Bar Chart**: Displays the "Member Activity" report as a stacked bar chart (total check-ins per club, stacked by month).
* **Dynamic Report Generation**: Generates "Member Activity" and "Popular Exercises" reports on the fly using Pandas.
* **Dual Format Export**: All reports are available in both JSON and CSV (with correct headers for file download).

---

## Setup and Installation

To get this project running locally, follow these steps.

### 1. Prerequisites

* Python 3.8+
* `pip` and `venv` (recommended)
* Node.js v16+ (`npm`)

### 2. Setup

#### Clone the repo
  ```bash
    git clone ___link____
    cd VGymExport
  ```
#### Backend Setup

1.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Install the required dependencies:**
    ```bash
    cd backend && pip install -r requirements.txt
    ```

#### FrontEnd Setup
  ```bash
  cd frontend && npm install
  ```

### 3. Generate Mock Data

Before running the API, you must generate the local mock data.

1.  **Generate base data (Clubs, Members, Check-ins):**
    ```bash
    python scripts/generate_data.py
    ```

2.  **Fetch API data (Exercises) and generate instances:**
    ```bash
    python scripts/fetch_exercises.py
    ```
    This will create all the necessary JSON files in the `/data` directory.

### 4. Run the Service

1. **Backend:**

  Once the data is generated, you can start the API server (from the backend folder).

  ```bash
  uvicorn main:app --reload
  ```
  the backend is accessible at http://127.0.0.1:8000  

2. **Frontend:**
  After spinning up the backend, we start the frontend. From the frontend folder, run the following command

  ```bash
  npm start
  ```
  The frontend UI can be accessed at http://localhost:3000



## API Endpoints
The service exposes two main endpoints. You can also see interactive documentation at http://127.0.0.1:8000/docs.

1. GET /api/exercises
Returns a paginated list of all exercises stored locally.

    #### Query Parameters:
    - offset (int, default: 0): The number of items to skip.
    - limit (int, default: 20): The number of items to return.

    #### Example Request:
    From a browser: [http://127.0.0.1:8000/api/exercises?offset=0&limit=2](http://127.0.0.1:8000/api/exercises?offset=0&limit=2)

    From command line utility
    ```
    curl "http://127.0.0.1:8000/api/exercises?offset=0&limit=2"
    ```
    #### Example Response (200 OK):

    ```
    {
    "count": 200,
    "next": "http://127.0.0.1:8000/api/exercises?offset=2&limit=2",
    "previous": null,
    "results": [
        {
        "exercise_id": "VPPtusI",
        "club_id": 5,
        "name": "inverted row bent knees",
        "target_muscles": [
            "upper back"
        ]
        },
        {
        "exercise_id": "8d8qJQI",
        "club_id": 1,
        "name": "barbell reverse grip incline bench row",
        "target_muscles": [
            "upper back"
        ]
        }
    ]
    }
    ```

2. GET /api/export
Generates and returns a specific report in the chosen format.

    #### Query Parameters:
    - type (required): The report to generate.
    - activity: Member check-ins grouped by club and month.

    #### popular-exercises: 
    Top 10 exercises per club by usage.

    #### format (required): 
    The output format. Can be eithr CSV or JSON as follows:
    - json: Returns a JSON array.
    - csv: Returns a text/csv file download.

    #### Example Request (JSON):

    ```
    curl "http://127.0.0.1:8000/api/export?type=activity&format=json"
    ```

    Example Response (JSON):

    ```
    [
        {
            "club_id": 1,
            "club_name": "Port Tannershire Fitness Center",
            "month_year": "2025-07",
            "total_checkins": 15
        },
        {
            "club_id": 1,
            "club_name": "Port Tannershire Fitness Center",
            "month_year": "2025-08",
            "total_checkins": 48
        },
        {
            "club_id": 1,
            "club_name": "Port Tannershire Fitness Center",
            "month_year": "2025-09",
            "total_checkins": 28
        },
    ]
    ```

    #### Example Request (CSV Download): This is best run in a browser. Pasting the URL in the address bar will trigger a file download.
    [http://127.0.0.1:8000/api/export?type=popular-exercises&format=csv](http://127.0.0.1:8000/api/export?type=popular-exercises&format=csv)


## Next Steps (TODOs)

* **Optimize File Storage:** If retaining files, switch from JSON to a columnar format like Parquet, which allows Pandas to read only the necessary columns for a report, drastically reducing memory usage.
* **Pre-calculate Reports:** Implement a nightly script to pre-aggregate reports, allowing the API to instantly serve these cached results instead of calculating them on every request, dramatically improving response time.
* **Asynchronous Exports:** Convert the export endpoint to a background job system (like Celery) to prevent API timeouts, allowing the server to immediately return a job ID and process large files without blocking.
* **Integrate a Database:** Replace in-memory JSON files with a real database (like PostgreSQL) to solve the primary memory bottleneck, enabling scalable, high-performance queries on massive datasets without loading everything into RAM.
* **Authentication**: Secure the endpoints using **OAuth2**, so only authorized managers can access the data.
* **Caching**: Implement **Redis** to cache the results of the ExerciseDB API call and possibly the generated reports to reduce load.