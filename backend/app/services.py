import pandas as pd
from pathlib import Path

# This path finds the 'data' folder at the project's root
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_data():
    """Loads all JSON data into a dictionary of Pandas DataFrames."""
    try:
        data = {
            "clubs": pd.read_json(DATA_DIR / "clubs.json"),
            "members": pd.read_json(DATA_DIR / "members.json"),
            "checkins": pd.read_json(DATA_DIR / "checkins.json"),
            "exercises": pd.read_json(DATA_DIR / "exercises.json"),
            "instances": pd.read_json(DATA_DIR / "exercise_instances.json")
        }
        
        # Convert timestamp columns
        data["checkins"]["timestamp"] = pd.to_datetime(data["checkins"]["timestamp"])
        data["instances"]["timestamp"] = pd.to_datetime(data["instances"]["timestamp"])
        
        print("All data loaded successfully.")
        return data
    except FileNotFoundError as e:
        print(f"ERROR: Missing data file {e.filename}. Please check the 'data' directory.")
        return None
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return None