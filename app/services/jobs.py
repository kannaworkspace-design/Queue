from app.repositories import jobs as repo

class UnknownJobType(Exception):
    pass

KNOWN_TYPES = ("send_email", "flaky")

async def enqueue(pool, type_, payload):
    if type_ not in KNOWN_TYPES:
        raise UnknownJobType()
    return await repo.insert(pool, type_, payload)

async def get(pool, job_id):
    return await repo.get(pool, job_id)