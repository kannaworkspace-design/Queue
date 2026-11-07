import asyncio
import json

from app.repositories import jobs as repo
from db import make_pool
from handlers import HANDLERS


POLL_SECONDS = 1
STALE_SECONDS = 30

async def run(name):
    pool = await make_pool()
    print(f"{name} started",flush=True)
    while True:
        job = await repo.claim(pool)
        if job is None:
            for job_id in await repo.reclaim_stale(pool, STALE_SECONDS):
                print(f"{name} put job {job_id} back in the queue")
            await asyncio.sleep(POLL_SECONDS)
            continue
        
        print(f"{name} picked job {job['id']} ({job['type']})")
        try:
            handler = HANDLERS[job["type"]]
            await handler(json.loads(job["payload"]))
        except Exception as e:
            status = await repo.mark_failed(pool, job["id"], str(e))
            print(f"{name} job {job['id']} errored -> {status}")
            continue
        await repo.mark_done(pool, job["id"])
        print(f"{name} finished job {job['id']}")
    