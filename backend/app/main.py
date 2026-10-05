from fastapi import FastAPI

from app.db.database import test_database_connection


app = FastAPI(
    title="IPO Application & Allotment Platform"
)


@app.get("/")
def root():
    return {
        "message": "IPO Platform API is running"
    }


@app.get("/health")
def health_check():
    database_name = test_database_connection()

    return {
        "status": "healthy",
        "database": database_name
    }