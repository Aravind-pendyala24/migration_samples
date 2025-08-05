from flask import Flask, request, jsonify
import subprocess
import os
import platform
import threading
import queue
import logging

app = Flask(__name__)

# Initialize queue for updates
update_queue = queue.Queue()

# Background worker to process queued jobs
def update_worker():
    while True:
        job = update_queue.get()
        if job is None:
            continue  # Skip if job is invalid

        xml_filename = job['xml_filename']
        arg1 = job['arg1']
        arg2 = job['arg2']
        xml_file_path = job['xml_file_path']
        script_path = job['script_path']

        command = ['bash', script_path, arg1, arg2, xml_file_path] if platform.system() == 'Windows' else ['sh', script_path, arg1, arg2, xml_file_path]

        app.logger.info(f"[WORKER] Running command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            app.logger.info(f"[WORKER] Command output for {xml_filename}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            app.logger.error(f"[WORKER] Subprocess error for {xml_filename}: {e}")
        except Exception as e:
            app.logger.error(f"[WORKER] Unexpected error for {xml_filename}: {e}")
        finally:
            update_queue.task_done()

# Start worker thread
threading.Thread(target=update_worker, daemon=True).start()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/update_xml', methods=['POST'])
def update_xml():
    data = request.json
    xml_filename = data.get('xml_filename')
    arg1 = data.get('arg1')
    arg2 = data.get('arg2')

    if not xml_filename or not arg1 or not arg2:
        return jsonify({"error": "Missing required parameters"}), 400

    xml_file_path = f'/usr/share/nginx/html/xml/{xml_filename}'
    script_path = '/usr/share/nginx/html/scripts/update_script.sh'

    if not os.path.exists(xml_file_path):
        return jsonify({"error": "XML file does not exist"}), 404

    if not os.path.exists(script_path):
        return jsonify({"error": "Script file does not exist"}), 404

    job = {
        "xml_filename": xml_filename,
        "arg1": arg1,
        "arg2": arg2,
        "xml_file_path": xml_file_path,
        "script_path": script_path
    }

    update_queue.put(job)
    app.logger.info(f"Queued update job for file: {xml_filename}")

    return jsonify({
        "status": "queued",
        "parameters": {
            "xml_filename": xml_filename,
            "arg1": arg1,
            "arg2": arg2
        }
    }), 202

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
