# test_concurrent.py

import requests
import threading

def send_post(i):
    response = requests.post("http://localhost:5000/update", json={"request_id": i})
    print(f"Request {i}: {response.json()}")

threads = []
for i in range(10):  # Simulate 10 concurrent requests
    t = threading.Thread(target=send_post, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
