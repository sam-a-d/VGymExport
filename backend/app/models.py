from enum import Enum

# Define allowed report types and formats
class ReportType(str, Enum):
    activity = "activity"
    popular_exercises = "popular-exercises"

class ReportFormat(str, Enum):
    json = "json"
    csv = "csv"