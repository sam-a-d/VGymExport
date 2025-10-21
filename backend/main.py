from app import create_app

# The Application Factory creates and configures the app
app = create_app()

# Uvicorn will look for this 'app' variable
# To run: uvicorn main:app --reload