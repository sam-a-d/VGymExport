import json
import random
import requests
import time 
from datetime import datetime, timedelta
from faker import Faker # We need faker for the exercise instances

# --- Configuration ---
API_URL = "https://exercisedb-api.vercel.app/api/v1/exercises"
EXERCISES_TO_FETCH = 200
NUM_INSTANCES = 1000
DATA_DIR = "../data/"

# Initialize Faker
fake = Faker()

# --- 1. Fetch Existing Member and Club Data ---
try:
    with open(f"{DATA_DIR}members.json", "r") as f:
        members = json.load(f)
    with open(f"{DATA_DIR}clubs.json", "r") as f:
        clubs = json.load(f)
except FileNotFoundError:
    print("Error: members.json or clubs.json not found.")
    print("Please run generate_data.py first.")
    exit()

# --- 2. Fetch Exercises from Public API with Pagination ---
print(f"Fetching {EXERCISES_TO_FETCH} exercises from ExerciseDB API...")
all_exercises = []
offset = 0
limit = 50  # Fetch in batches of 50

while len(all_exercises) < EXERCISES_TO_FETCH:
    try:
        # Make the API call with pagination parameters
        response = requests.get(f"{API_URL}?limit={limit}&offset={offset}", timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        batch = response.json()['data']
        
        # --- CHANGE 2: Check if the response is a list ---
        if isinstance(batch, list):
            if not batch:
                print("  No more exercises found. Stopping.")
                break # Stop if the API returns an empty list
            
            all_exercises.extend(batch)
            offset += limit
            print(f"  Fetched {len(all_exercises)}/{EXERCISES_TO_FETCH} exercises...")
        else:
            # If the API returns an object or something else, log it and stop.
            print(f"  Received unexpected data (not a list): {batch}. Stopping.")
            break
        # --- End of CHANGE 2 ---

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}. Stopping.")
        break
    
    ########### Important: Wait 1 second to avoid rate-limiting ---
    time.sleep(1)
 

# Trim the list to exactly the number we want
exercises_data = all_exercises[:EXERCISES_TO_FETCH]

# --- 3. Process and Save Exercises ---
print(f"\nProcessing {len(exercises_data)} exercises...")
processed_exercises = []
for exercise in exercises_data:
    # Add a safety check in case any bad data still got through
    if not isinstance(exercise, dict):
        print(f"  Skipping invalid exercise data: {exercise}")
        continue
        
    processed_exercises.append({
        "exercise_id": exercise.get("exerciseId"),
        "club_id": random.choice(clubs)["club_id"],
        "name": exercise.get("name"),
        "target_muscles": exercise.get("targetMuscles"),
    })

with open(f"{DATA_DIR}exercises.json", "w") as f:
    json.dump(processed_exercises, f, indent=4)
print(f" Saved {len(processed_exercises)} exercises to exercises.json.")


# --- 4. Generate Exercise Instances ---
print(f"\nGenerating {NUM_INSTANCES} exercise instances...")
exercise_instances = []

# Ensure we have exercises to sample from
if not processed_exercises:
    print("No exercises were processed. Cannot generate instances.")
    exit()

for i in range(1, NUM_INSTANCES + 1):
    random_member = random.choice(members)
    random_exercise = random.choice(processed_exercises)
    
    exercise_instances.append({
        "instance_id": i,
        "member_id": random_member["member_id"],
        "exercise_id": random_exercise["exercise_id"],
        "club_id": random_member["club_id"],
        "timestamp": fake.date_time_between(start_date=datetime.now() - timedelta(days=120), end_date=datetime.now()).isoformat()
    })

with open(f"{DATA_DIR}exercise_instances.json", "w") as f:
    json.dump(exercise_instances, f, indent=4)
print(f" Generated {len(exercise_instances)} exercise instances.")

print("\n API integration and data generation complete!")