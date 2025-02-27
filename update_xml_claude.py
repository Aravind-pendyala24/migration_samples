from flask import Flask, request, jsonify
import subprocess
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to your mounted directories
BASE_PATH = "/usr/share/nginx/html"
XML_DIR = os.path.join(BASE_PATH, "xml")
SCRIPTS_DIR = os.path.join(BASE_PATH, "scripts")

@app.route('/update-xml', methods=['POST'])
def update_xml():
    try:
        # Get parameters from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract required parameters
        xml_file = data.get('xml_file')
        arg1 = data.get('arg1')
        arg2 = data.get('arg2')
        script_name = data.get('script_name', 'update_xml.sh')
        
        # Validate parameters
        if not xml_file or not arg1 or not arg2:
            return jsonify({"error": "Missing required parameters"}), 400
            
        # Ensure the XML file path is valid and within the XML directory
        xml_path = os.path.join(XML_DIR, xml_file)
        if not os.path.exists(xml_path):
            return jsonify({"error": f"XML file not found: {xml_file}"}), 404
            
        # Ensure the script exists
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        if not os.path.exists(script_path):
            return jsonify({"error": f"Script not found: {script_name}"}), 404
            
        # Ensure the script is executable
        if not os.access(script_path, os.X_OK):
            logger.info(f"Script not executable, attempting to make it executable: {script_path}")
            os.chmod(script_path, 0o755)
            
        # Execute the shell script with arguments
        logger.info(f"Executing script: {script_path} with args: {xml_path} {arg1} {arg2}")
        result = subprocess.run([script_path, xml_path, arg1, arg2], 
                               capture_output=True, text=True, check=False)
        
        # Check if the script executed successfully
        if result.returncode != 0:
            logger.error(f"Script execution failed: {result.stderr}")
            return jsonify({
                "success": False,
                "error": result.stderr,
                "message": "Script execution failed"
            }), 500
            
        # Return success response
        return jsonify({
            "success": True,
            "message": "XML file updated successfully",
            "details": result.stdout
        })
            
    except Exception as e:
        logger.exception("Error occurred during XML update")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Internal server error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
