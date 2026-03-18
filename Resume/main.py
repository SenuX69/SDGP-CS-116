from fastapi import FastAPI
from routes.cv_routes import router as cv_router

app = FastAPI()

app.include_router(cv_router)

@app.get("/")
def root():
    return {"message": "Resume Parser API running"}