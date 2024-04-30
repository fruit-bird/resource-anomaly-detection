import requests
import time

while True:
    requests.get("http://localhost:8000/metrics")
    time.sleep(0.5)
