from flask import Flask, request, jsonify
import subprocess
import os
import platform
import threading
import queue
import logging
import uuid

# ------------------------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------------------------
app = Flask(__name__)
update_queue = queue.Queue()

# ------------------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Capture INFO, WARNING, ERROR, etc.
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]  # Log to stdout
)

# Apply to Flask's app logger
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)

logger = app.logger

# ------------------------------------------------------------------------------
# Background Worker Function
# ------------------------------------------------------------------------------
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
        command = ['sh', script_path, arg1, arg2, xml_file_path]

        logger.info("\n" + "=" * 80)
        logger.info(f"🟢 START JOB  | JobID: {job_id}")
        logger.info(f"📄 Target XML: {xml_filename}")
        logger.info(f"⚙️  Command   : {' '.join(command)}")
        logger.info("-" * 80)

        try:
            result = subprocess.run(command, capture_output=True, text=True, stderr=subprocess.STDOUT)
            output = result.stdout.strip()
            if output:
                logger.info(f"✅ [Job {job_id}] Shell Output:\n{output}")
            else:
                logger.warning(f"⚠️  [Job {job_id}] No output returned from shell script.")

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ [Job {job_id}] Subprocess failed:\n{e.stderr or str(e)}")

        except Exception as e:
            logger.exception(f"❌ [Job {job_id}] Unexpected error:")

        finally:
            logger.info(f"✅ END JOB    | JobID: {job_id}")
            logger.info("=" * 80 + "\n")
            update_queue.task_done()

# ------------------------------------------------------------------------------
# Start Background Worker
# ------------------------------------------------------------------------------
threading.Thread(target=update_worker, daemon=True).start()

# ------------------------------------------------------------------------------
# Health Check Route
# ------------------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# ------------------------------------------------------------------------------
# Main API Route
# ------------------------------------------------------------------------------
@app.route('/update_xml', methods=['POST'])
def update_xml():
    data = request.json
    xml_filename = data.get('xml_filename')
    arg1 = data.get('arg1')
    arg2 = data.get('arg2')

    if not xml_filename or not arg1 or not arg2:
        logger.warning("⚠️  [API] Missing parameters in request")
        return jsonify({"error": "Missing required parameters"}), 400

    xml_file_path = f'/usr/share/nginx/html/xml/{xml_filename}'
    script_path = '/usr/share/nginx/html/scripts/update_script.sh'

    if not os.path.exists(xml_file_path):
        logger.error(f"❌ [API] XML file does not exist: {xml_file_path}")
        return jsonify({"error": "XML file does not exist"}), 404

    if not os.path.exists(script_path):
        logger.error(f"❌ [API] Script file does not exist: {script_path}")
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
    logger.info(f"📬 [API] Job queued | JobID: {job_id} | File: {xml_filename} | Args: ({arg1}, {arg2})")

    return jsonify({
        "status": "queued",
        "job_id": job_id,
        "parameters": {
            "xml_filename": xml_filename,
            "arg1": arg1,
            "arg2": arg2
        }
    }), 202
#Run tha app
#gunicorn -w 4 -b 0.0.0.0:5000 app:app --log-level info --access-logfile -
