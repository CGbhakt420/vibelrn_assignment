from fastapi import FastAPI
from app.api.routes import router
from app.database.config import engine, Base

app = FastAPI(
    title="Reviews API",
    description="FastAPI application for managing review history with categories",
    version="1.0.0"
)


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/")
async def root():
    return {
        "message": "Reviews API",
        "endpoints": {
            "trends": "/reviews/trends",
            "reviews_by_category": "/reviews/?category_id=<category_id>"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
