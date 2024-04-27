from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import datetime
import psutil
import asyncpg
import os
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    db_url = os.environ.get("DB_URL")
    app.state.pool = await asyncpg.create_pool(db_url)
    yield
    # Shutdown event
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent
        network_usage = psutil.net_io_counters()
        now = datetime.datetime.now()

        async with app.state.pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO metrics (cpu_percent, memory_percent, disk_usage, bytes_sent, bytes_recv, time) VALUES ($1, $2, $3, $4, $5, $6)",
                cpu_percent,
                memory_percent,
                disk_usage,
                network_usage.bytes_sent,
                network_usage.bytes_recv,
                now,
            )

        return {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_usage,
            "network": {
                "bytes_sent": network_usage.bytes_sent,
                "bytes_recv": network_usage.bytes_recv,
            },
            "time": now.isoformat(),
        }
    except Exception as e:
        logger.error("Error fetching or inserting metrics: %s", e)
        raise HTTPException(status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
