from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Path to your shell script. Make sure this is the absolute path where the script resides.
SHELL_SCRIPT = '/mnt/scripts/update-xml.sh'

@app.route('/api/update-xml', methods=['POST'])
def update_xml():
    # Get JSON data from the request.
    data = request.get_json()
    if not data or 'arg1' not in data or 'arg2' not in data:
        return jsonify({'error': 'Both arg1 and arg2 are required.'}), 400

    arg1 = data['arg1']
    arg2 = data['arg2']

    try:
        # Call the shell script with the provided arguments.
        # The subprocess.run command executes the script and waits for it to finish.
        result = subprocess.run(
            [SHELL_SCRIPT, arg1, arg2],
            capture_output=True,      # Capture stdout and stderr.
            text=True,                # Return output as strings.
            check=True                # Raise CalledProcessError if the command fails.
        )
        # Return the output from the shell script if needed.
        return jsonify({
            'message': 'XML file updated successfully!',
            'output': result.stdout
        }), 200
    except subprocess.CalledProcessError as e:
        # If the shell script returns an error, capture its output and return it.
        return jsonify({
            'error': 'Failed to update XML file.',
            'details': e.stderr
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
