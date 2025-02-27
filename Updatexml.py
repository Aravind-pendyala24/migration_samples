from flask import Flask, request, jsonify
import os
import fcntl

app = Flask(__name__)

# Path to the XML file on the shared persistent volume.
# In this example, the XML file is stored at /mnt/xmls/config.xml.
XML_FILE = '/mnt/xmls/config.xml'

@app.route('/api/update-xml', methods=['POST'])
def update_xml():
    # Retrieve the JSON data sent in the POST request.
    data = request.get_json()
    
    # Validate that the required keys (arg1 and arg2) are present.
    if not data or 'arg1' not in data or 'arg2' not in data:
        # Return a JSON error response with HTTP status 400 (Bad Request)
        return jsonify({'error': 'Both arg1 and arg2 are required.'}), 400

    # Extract the two input arguments from the JSON payload.
    arg1 = data['arg1']
    arg2 = data['arg2']

    # Construct the new XML content using an f-string.
    # This creates an XML structure with <param1> and <param2> elements.
    new_xml = f"""<root>
  <param1>{arg1}</param1>
  <param2>{arg2}</param2>
</root>"""

    try:
        # Open the XML file in write mode.
        with open(XML_FILE, 'w') as f:
            # Acquire an exclusive file lock to prevent concurrent writes.
            # This ensures that if multiple requests come in at the same time,
            # only one can update the file at a time.
            fcntl.flock(f, fcntl.LOCK_EX)
            
            # Write the new XML content to the file.
            f.write(new_xml)
            # Flush the file buffer to ensure data is written immediately.
            f.flush()
            
            # Release the file lock.
            fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        # If any error occurs during file access or writing, return a 500 error.
        return jsonify({'error': str(e)}), 500

    # If everything goes smoothly, return a success message.
    return jsonify({'message': 'XML file updated successfully!'}), 200

# The main entry point of the script.
if __name__ == '__main__':
    # Start the Flask app, binding to all network interfaces on port 3000.
    app.run(host='0.0.0.0', port=3000)
