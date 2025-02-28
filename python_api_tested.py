from flask import Flask, request, jsonify
import subprocess
import os
import platform

app = Flask(__name__)

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

    command = ['bash', script_path, arg1, arg2, xml_file_path] if platform.system() == 'Windows' else ['sh', script_path, arg1, arg2, xml_file_path]

    app.logger.info(f"Running command: {' '.join(command)}")
    app.logger.info(f"Parameters - xml_filename: {xml_filename}, arg1: {arg1}, arg2: {arg2}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        app.logger.info(f"Command output: {result.stdout}")
        return jsonify({
            "output": result.stdout,
            "parameters": {
                "xml_filename": xml_filename,
                "arg1": arg1,
                "arg2": arg2
            }
        })
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Subprocess error: {e}")
        return jsonify({
            "error": "Subprocess error",
            "details": str(e),
            "output": e.output,
            "parameters": {
                "xml_filename": xml_filename,
                "arg1": arg1,
                "arg2": arg2
            }
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Unexpected error",
            "details": str(e),
            "parameters": {
                "xml_filename": xml_filename,
                "arg1": arg1,
                "arg2": arg2
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
