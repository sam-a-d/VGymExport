from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our new modules
from app.services import load_data
from app.routers import export, exercise

def create_app():
    """
    The Application Factory.
    """
    
    # 1. Create the FastAPI app instance
    app = FastAPI(
        title="Virtuagym Export Service",
        description="A service to export gym reports in different formats.",
        version="1.0.0"
    )

    # 2. Add Middleware
    origins = ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Load data on startup and store it in the app's 'state'
    # This is how we share the 'db' connection with our endpoints
    db = load_data()
    if db is None:
        print("Failed to load data, exiting.")
        exit()
    app.state.db = db

    # 4. Include the routers
    app.include_router(exercise.router, tags=["Exercises"])
    app.include_router(export.router, tags=["Export"])

    # 5. Add the root endpoint
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the Virtuagym Export Service!"}

    return app