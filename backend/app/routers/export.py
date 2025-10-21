import pandas as pd
from io import StringIO
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

# Import our new models
from app.models import ReportType, ReportFormat

# 1. Create the router
router = APIRouter()

# 2. Move your helper function here
def create_csv_response(df: pd.DataFrame, filename: str):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(csv_buffer, media_type="text/csv", headers=headers)

# 3. Move the export endpoint here
@router.get("/api/export")
def get_export(
    type: ReportType,
    format: ReportFormat,
    request: Request  # We add Request to access the 'db'
):
    """
    Generates and returns a dataset based on the report type and format.
    """
    # 4. Get the 'db' from the app's state
    db = request.app.state.db

    if type == ReportType.activity:
        df = pd.merge(db["checkins"], db["clubs"], on="club_id", how="left")
        df["month_year"] = df["timestamp"].dt.to_period("M").astype(str)
        report = df.groupby(
            ["club_id", "club_name", "month_year"]
        ).size().reset_index(name="total_checkins")
        filename = "member_activity.csv"

    elif type == ReportType.popular_exercises:
        exercise_names = db["exercises"][["exercise_id", "name"]]
        df = pd.merge(db["instances"], exercise_names, on="exercise_id", how="left")
        df = pd.merge(df, db["clubs"], on="club_id", how="left")
        usage_counts = df.groupby(
            ["club_id", "club_name", "exercise_id", "name"]
        ).size().reset_index(name="usage_count")
        report = usage_counts.sort_values(
            by=["club_id", "usage_count"], ascending=[True, False]
        ).groupby("club_id").head(10).reset_index(drop=True)
        filename = "popular_exercises.csv"

    else:
        raise HTTPException(status_code=400, detail="Invalid report type.")

    if format == ReportFormat.json:
        return JSONResponse(content=report.to_dict("records"))
    
    elif format == ReportFormat.csv:
        return create_csv_response(report, filename)