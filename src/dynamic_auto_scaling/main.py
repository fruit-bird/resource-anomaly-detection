from fastapi import FastAPI
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
    try:
        yield
    finally:
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
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    network_usage = psutil.net_io_counters()
    now = datetime.datetime.now()

    metrics = {
        "cpu": cpu_percent,
        "memory": memory_percent,
        "disk": disk_usage,
        "network": {
            "bytes_sent": network_usage.bytes_sent,
            "bytes_recv": network_usage.bytes_recv,
        },
        "time": now,
    }

    async with app.state.pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO metrics (cpu_percent, memory_percent, disk_usage, bytes_sent, bytes_recv, time) VALUES ($1, $2, $3, $4, $5, $6)",
            metrics["cpu"],
            metrics["memory"],
            metrics["disk"],
            metrics["network"]["bytes_sent"],
            metrics["network"]["bytes_recv"],
            metrics["time"],
        )
    return metrics


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
