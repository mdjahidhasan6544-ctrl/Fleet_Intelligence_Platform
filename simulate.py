import requests
import time
import random
from datetime import datetime, timezone

API_URL = "http://localhost:8000/api/v1/ingest/"
API_KEY = "test-key-123"

def simulate_device(lat, lng):
    fuel = 100.0
    while True:
        lat += random.uniform(-0.005, 0.005)
        lng += random.uniform(-0.005, 0.005)
        speed = random.uniform(40, 80)
        
        fuel -= random.uniform(0.1, 0.5)
        if random.random() < 0.05:
            fuel -= 15.0

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": lat,
            "longitude": lng,
            "speed": speed,
            "fuel_level": max(0, fuel)
        }
        
        headers = {"X-API-Key": API_KEY}
        try:
            res = requests.post(API_URL, json=payload, headers=headers)
            print(f"Sent: {res.status_code} - {payload['latitude']}, {payload['longitude']}")
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    print("Starting simulator...")
    simulate_device(34.0522, -118.2437)
