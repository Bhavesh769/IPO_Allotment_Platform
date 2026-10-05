from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import create_tables, test_database_connection

from app.api.routes.applications import router as applications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="IPO Application & Allotment Platform",
    lifespan=lifespan,
)

app.include_router(applications_router)

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