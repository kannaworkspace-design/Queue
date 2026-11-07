# Jobline

A job queue built on Postgres. An API takes jobs in. A separate worker process
takes them out and runs them.

Built so that slow work — sending an email, generating a file — happens outside
the web request, and no job is lost if a worker crashes while holding it.

**API:** https://jobline-api.onrender.com/docs
**Worker:** https://jobline-worker.onrender.com/health

---

## Try it in 30 seconds

Free hosting, so both services sleep when idle. Wake the worker first.

**1.** Open the **Worker** link above. Wait for `{"status":"ok"}`. First load takes about a minute.

**2.** Open the **API** link. Find `POST /jobs` → *Try it out* → paste this → *Execute*:

```json
{
  "type": "send_email",
  "payload": { "to": "you@example.com" }
}
```

You get back a job with `"status": "queued"` and an `id`.

**3.** Find `GET /jobs/{job_id}`, put that `id` in, *Execute*.

Within a few seconds it reads `"status": "done"` and `"attempts": 1`.

The worker picked it up, ran it, and marked it finished. Nothing was waiting on it.

**Also try:** send `"type": "flaky"` with payload `{}`. That job always fails. Check it
a few times and watch `attempts` climb to 3, then `status` settle on `failed` with
the error stored in `last_error`. It does not retry forever, and it does not vanish.

---

## What it handles

**Many workers at once.** Claiming a job is one `UPDATE` with `FOR UPDATE SKIP LOCKED`,
so two workers never take the same job.

> Measured with 20 workers and 200 jobs: the obvious two-statement version
> (`SELECT` a job, then `UPDATE` it) claimed those 200 jobs **2,952 times** — every
> job done about fifteen times. This version claims each job exactly once.

**Jobs that fail.** Retried up to `max_attempts`, then parked as `failed` with the
error stored.

**Workers that die.** Each claim stamps `claimed_at`. A job still marked `running`
long after it was claimed gets put back in the queue by any other worker.

> Verified with `kill -9` on a worker holding a 20-second job. The job was stuck at
> `running`, a second worker put it back 12 seconds later, and it completed.

---

## What it does not do

**At-least-once, not exactly-once.** A worker killed between finishing the work and
marking it done will cause a repeat. Handlers must be safe to run twice.

**No backoff.** Retries happen immediately rather than waiting longer each time.

---

## Why Postgres and not Redis

Redis is faster and purpose-built, but Postgres was already here and `SKIP LOCKED`
makes it correct. Render's free Redis is memory-only — it loses everything on
restart, and losing jobs is the one thing this service exists to prevent.

At tens of thousands of jobs per second the answer changes.

---

## Stack

Python, FastAPI, PostgreSQL (Neon), asyncpg. Deployed on Render as two services.

## Run it locally

```bash
pip install -r requirements.txt
psql "$DATABASE_URL" -f schema.sql

uvicorn main:app --reload     # terminal 1
python worker.py w1           # terminal 2
```
