from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import jobs
from db import make_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await make_pool()
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan, title="Jobline")
app.include_router(jobs.router)

@app.get("/health")
async def health():
    return {"status": "ok"}