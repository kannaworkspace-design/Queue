import asyncio
import sys
from worker_loop import run


name = sys.argv[1] if len(sys.argv) > 1 else "worker"

asyncio.run(run(name))