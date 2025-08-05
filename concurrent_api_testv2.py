from flask import Flask, request, jsonify
import subprocess
import os
import platform
import threading
import queue
import logging
import uuid

app = Flask(__name__)

# Queue for serialized updates
update_queue = queue.Queue()

# ------------------------------
# Configure clean & structured logging
# ------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=[logging.StreamHandler()])
logger = app.logger

# ------------------------------
# Background Worker Thread
# ------------------------------
def update_worker():
    while True:
        job = update_queue.get()
        if job is None:
            continue

        job_id = job['job_id']
        xml_filename = job['xml_filename']
        arg1 = job['arg1']
        arg2 = job['arg2']
        xml_file_path = job['xml_file_path']
        script_path = job['script_path']

        command = ['bash', script_path, arg1, arg2, xml_file_path] if platform.system() == 'Windows' else ['sh', script_path, arg1, arg2, xml_file_path]

        logger.info("\n" + "=" * 80)
        logger.info(f"START JOB | JobID: {job_id}")
        logger.info(f"Target XML: {xml_filename}")
        logger.info(f"Command : {' '.join(command)}")
        logger.info("-" * 80)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info(f"[Job {job_id}] Shell Output:\n{result.stdout.strip() or '[No output]'}")
        except subprocess.CalledProcessError as e:
            logger.error(f"[Job {job_id}] Subprocess failed:\n{e.stderr or str(e)}")
        except Exception as e:
            logger.error(f"[Job {job_id}] Unexpected error:\n{str(e)}")
        finally:
            logger.info(f"END JOB | JobID: {job_id}")
            logger.info("=" * 80 + "\n")
            update_queue.task_done()

# Start background worker thread
threading.Thread(target=update_worker, daemon=True).start()

# ------------------------------
# Flask Routes
# ------------------------------

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

    job_id = str(uuid.uuid4())[:8]

    job = {
        "job_id": job_id,
        "xml_filename": xml_filename,
        "arg1": arg1,
        "arg2": arg2,
        "xml_file_path": xml_file_path,
        "script_path": script_path
    }

    update_queue.put(job)
    logger.info(f"[API] Job queued | JobID: {job_id} | File: {xml_filename} | Args: ({arg1}, {arg2})")

    return jsonify({
        "status": "queued",
        "job_id": job_id,
        "parameters": {
            "xml_filename": xml_filename,
            "arg1": arg1,
            "arg2": arg2
        }
    }), 202

# ------------------------------
# App Runner
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
