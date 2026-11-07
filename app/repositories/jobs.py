import json

async def insert(pool, type_, payload):
    return await pool.fetchrow(
    """
    INSERT INTO jobs (type, payload)
    VALUES ($1, $2)
    RETURNING *
    """,
    type_,
    json.dumps(payload),
    )
async def get(pool, job_id):
    return await pool.fetchrow("SELECT * FROM jobs WHERE id = $1", job_id)

async def claim(pool):
    return await pool.fetchrow(
        """
        UPDATE jobs
        SET status = 'running',
        attempts = attempts + 1,
        claimed_at = now()
        WHERE id = (
        SELECT id FROM jobs
        WHERE status = 'queued'
        ORDER BY id
        LIMIT 1
        FOR UPDATE SKIP LOCKED
        )
        RETURNING *
        """
    )

async def mark_done(pool, job_id):
    await pool.execute("UPDATE jobs SET status = 'done' WHERE id = $1", job_id)

async def mark_failed(pool, job_id, error):
    return await pool.fetchval(
        """
        UPDATE jobs
        SET status = CASE WHEN attempts >= max_attempts
        THEN 'failed'
        ELSE 'queued' END,
        last_error = $2,
        claimed_at = NULL
        WHERE id = $1
        RETURNING status
        """,
        job_id,
        error,
    )

async def reclaim_stale(pool, stale_seconds):
    rows = await pool.fetch(
        """
        UPDATE jobs
        SET status = 'queued',
        claimed_at = NULL
        WHERE status = 'running'
        AND claimed_at < now() - ($1 * INTERVAL '1 second')
        RETURNING id
        """,
        stale_seconds,
    )
    return [r["id"] for r in rows]