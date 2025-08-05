import requests
import threading
import time

# CONFIGURATION
URL = "http://localhost:5000/update_xml"
XML_FILENAME = "list.xml"  # Must exist in /usr/share/nginx/html/xml/

# Two argument lists (must be of equal length)
arg1_list = ["1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.4.0"]
arg2_list = ["AQWD", "RSUSPRD", "IESA", "OYJI", "MJNH"]

# Ensure both lists have the same number of elements
if len(arg1_list) != len(arg2_list):
    raise ValueError("arg1_list and arg2_list must be the same length.")

NUM_REQUESTS = len(arg1_list)

def send_post(arg1, arg2):
    payload = {
        "xml_filename": XML_FILENAME,
        "arg1": arg1,
        "arg2": arg2
    }
    try:
        response = requests.post(URL, json=payload)
        print(f"Sent arg1={arg1}, arg2={arg2} → Status {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"Request with arg1={arg1}, arg2={arg2} failed with exception: {e}")

threads = []
start_time = time.time()

for i in range(NUM_REQUESTS):
    t = threading.Thread(target=send_post, args=(arg1_list[i], arg2_list[i]))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Completed {NUM_REQUESTS} requests in {time.time() - start_time:.2f} seconds.")
