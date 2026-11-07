import asyncio

async def send_email(payload):
    await asyncio.sleep(1)
    print(f" sent email to {payload['to']}")

async def flaky(payload):
    raise RuntimeError("mail server refused the connection")


HANDLERS = {
"send_email": send_email,
"flaky": flaky,
}