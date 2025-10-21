from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# 1. Create the router
router = APIRouter()

# 2. Move your endpoint here, using @router.get instead of @app.get
@router.get("/api/exercises")
def get_exercises(request: Request, offset: int = 0, limit: int = 20):
    """
    Returns a paginated list of the locally stored exercises, 
    including next and previous page links.
    """
    # 3. Get the 'db' from the app's state
    db = request.app.state.db
    
    total_exercises = len(db["exercises"])
    paginated_exercises = db["exercises"].iloc[offset : offset + limit]
    
    # --- Logic to build next and previous URLs ---
    next_url = None
    if offset + limit < total_exercises:
        next_offset = offset + limit
        next_url = f"{request.base_url}{request.url.path.lstrip('/')}?offset={next_offset}&limit={limit}"

    previous_url = None
    if offset > 0:
        previous_offset = max(0, offset - limit)
        previous_url = f"{request.base_url}{request.url.path.lstrip('/')}?offset={previous_offset}&limit={limit}"
    
    response_data = {
        "count": total_exercises,
        "next": next_url,
        "previous": previous_url,
        "results": paginated_exercises.to_dict("records")
    }
    
    return JSONResponse(content=response_data)