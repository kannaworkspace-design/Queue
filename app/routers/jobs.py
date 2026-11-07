from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.services import jobs as service
router = APIRouter(prefix="/jobs")

class NewJob(BaseModel):
    type: str
    payload: dict


@router.post("", status_code=201)
async def create(body: NewJob, request: Request):
    try:
        job = await service.enqueue(request.app.state.pool, body.type, body.payload)
    except service.UnknownJobType:
        raise HTTPException(status_code=400, detail="unknown job type")
    return dict(job)


@router.get("/{job_id}")
async def read(job_id: int, request: Request):
    job = await service.get(request.app.state.pool, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="no such job")
    return dict(job)