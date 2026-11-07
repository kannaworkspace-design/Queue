import asyncio
from contextlib import asynccontextmanager


from fastapi import FastAPI
from worker_loop import run

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.task = asyncio.create_task(run("render-worker"))
    yield
    app.state.task.cancel()


app = FastAPI(lifespan=lifespan, title="Jobline worker")

@app.get("/health")
async def health():
    return {"status": "ok"}