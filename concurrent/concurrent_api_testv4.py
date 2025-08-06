from flask import Flask, request, jsonify
import subprocess
import os
import platform
import logging
import fasteners  # 👈 For inter-process locking
import time

app = Flask(__name__)

# Setup Logging
logger = logging.getLogger()
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
app.logger.handlers = logger.handlers
app.logger.setLevel(logging.INFO)

# Path for lockfile (can be shared by all requests)
LOCKFILE_PATH = "/tmp/update_script.lock"

@app.route('/health', methods=['GET'])
def health_check():
    app.logger.info("Health check called")
    return jsonify({"status": "healthy"}), 200

@app.route('/update_xml', methods=['POST'])
def update_xml():
    data = request.json
    xml_filename = data.get('xml_filename')
    arg1 = data.get('arg1')
    arg2 = data.get('arg2')

    if not xml_filename or not arg1 or not arg2:
        app.logger.warning("Missing parameters in request")
        return jsonify({"error": "Missing required parameters"}), 400

    xml_file_path = f'/usr/share/nginx/html/xml/{xml_filename}'
    script_path = '/usr/share/nginx/html/scripts/update_script.sh'

    if not os.path.exists(xml_file_path):
        app.logger.error(f"XML file does not exist: {xml_file_path}")
        return jsonify({"error": "XML file does not exist"}), 404

    if not os.path.exists(script_path):
        app.logger.error(f"Script file does not exist: {script_path}")
        return jsonify({"error": "Script file does not exist"}), 404

    # Prepare the command
    command = ['sh', script_path, arg1, arg2, xml_file_path] if platform.system() != 'Windows' \
        else ['bash', script_path, arg1, arg2, xml_file_path]

    # Acquire inter-process lock before running the script
    lock = fasteners.InterProcessLock(LOCKFILE_PATH)
    if lock.acquire(blocking=True, timeout=30):  # Wait max 30 seconds
        try:
            app.logger.info(f"🔒 Lock acquired. Running command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            app.logger.info(f"✅ Successfully updated: {xml_filename}")
            return jsonify({
                "message": "File updated successfully",
                "output": result.stdout.strip(),
                "parameters": {
                    "xml_filename": xml_filename,
                    "arg1": arg1,
                    "arg2": arg2
                }
            }), 200
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Script failed: {e}")
            return jsonify({
                "error": "Script execution failed",
                "details": str(e),
                "output": e.output.strip()
            }), 500
        finally:
            lock.release()
            app.logger.info("🔓 Lock released.")
    else:
        app.logger.warning("Could not acquire lock within timeout.")
        return jsonify({
            "error": "Could not acquire lock. Try again later."
        }), 429  # Too many requests / conflict
