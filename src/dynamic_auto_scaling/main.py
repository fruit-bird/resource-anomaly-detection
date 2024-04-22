from fastapi import FastAPI
import datetime
import psutil

app = FastAPI()


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    network_usage = psutil.net_io_counters()

    return {
        "cpu": cpu_percent,
        "memory": memory_percent,
        "disk": disk_usage,
        "network": {
            "bytes_sent": network_usage.bytes_sent,
            "bytes_recv": network_usage.bytes_recv,
        },
        "timestamp": datetime.datetime.now().isoformat(),
    }
