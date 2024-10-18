import os
from flask import Flask, request, jsonify
import docker

app = Flask(__name__)
client = docker.from_env()

controller_ip = os.getenv("CONTROLLER_IP", "0.0.0.0")
controller_port = int(os.getenv("CONTROLLER_PORT", "5000"))

@app.route('/create_container', methods=['POST'])
def create_container():
    data = request.get_json()
    image = data.get('image')
    ports = data.get('ports')
    try:
        container = client.containers.run(image, detach=True, ports=ports)
        return jsonify({"status": "success", "container_id": container.id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Agent is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=controller_port)
