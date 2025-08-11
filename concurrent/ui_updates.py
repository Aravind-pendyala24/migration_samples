import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

API_URL = "http://localhost:5000/update_xml"  # Change to your AKS endpoint if needed

def send_request():
    xml_filename = xml_filename_entry.get().strip()
    arg1 = arg1_entry.get().strip()
    arg2 = arg2_entry.get().strip()

    if not xml_filename or not arg1 or not arg2:
        messagebox.showerror("Error", "All fields are required")
        return

    payload = {
        "xml_filename": xml_filename,
        "arg1": arg1,
        "arg2": arg2
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        result_text.delete(1.0, tk.END)  # Clear previous text
        result_text.insert(tk.END, json.dumps(response.json(), indent=4))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Failed", str(e))

# ---- UI Setup ----
root = tk.Tk()
root.title("Update XML API Trigger")
root.geometry("600x400")

# Form Fields
ttk.Label(root, text="XML Filename:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
xml_filename_entry = ttk.Entry(root, width=40)
xml_filename_entry.grid(row=0, column=1, pady=5)

ttk.Label(root, text="Arg1:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
arg1_entry = ttk.Entry(root, width=40)
arg1_entry.grid(row=1, column=1, pady=5)

ttk.Label(root, text="Arg2:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
arg2_entry = ttk.Entry(root, width=40)
arg2_entry.grid(row=2, column=1, pady=5)

# Submit Button
submit_button = ttk.Button(root, text="Send Request", command=send_request)
submit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result Box
ttk.Label(root, text="Response:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
result_text = tk.Text(root, height=10, width=70)
result_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
