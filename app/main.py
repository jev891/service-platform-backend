from fastapi import FastAPI
from app.routes.users import router as user_router

app = FastAPI()

# Add root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Service Platform API"}

# Include user routes
app.include_router(user_router, prefix="/api")


# Start server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
