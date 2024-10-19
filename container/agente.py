import os
import platform
import socket
import requests
from flask import Flask, request, jsonify
import threading
import time
import docker
import subprocess
import base64


app = Flask(__name__)
client = docker.from_env()

# Variáveis de ambiente
controller_ip = os.getenv("CONTROLLER_IP", "127.0.0.1")
controller_port = int(os.getenv("CONTROLLER_PORT", "5050"))
agent_port = int(os.getenv("AGENT_PORT", "5000"))

# Obter informações do agente
agent_name = socket.gethostname()
agent_ip = socket.gethostbyname(socket.gethostname())
agent_os = platform.system()

# Função para registrar o agente no controlador
def register_agent():
    registration_url = f"http://{controller_ip}:{controller_port}/register_agent"
    data = {
        "agent_name": agent_name,
        "agent_ip": agent_ip,
        "agent_port": agent_port,
        "agent_os": agent_os
    }
    while True:
        try:
            response = requests.post(registration_url, json=data)
            if response.status_code == 200:
                print("Agente registrado com sucesso no controlador.")
                break
            else:
                print(f"Falha ao registrar agente: {response.text}")
        except Exception as e:
            print(f"Erro ao conectar ao controlador: {e}")
        time.sleep(10)  # Tentar novamente em 10 segundos

# Função para enviar heartbeat ao controlador
def send_heartbeat():
    heartbeat_url = f"http://{controller_ip}:{controller_port}/agent_heartbeat"
    data = {
        "agent_name": agent_name,
        "agent_ip": agent_ip,
        "agent_port": agent_port,
        "agent_os": agent_os
    }
    while True:
        try:
            response = requests.post(heartbeat_url, json=data)
            if response.status_code == 200:
                print(f"Heartbeat enviado para {controller_ip}:{controller_port}")
            else:
                print(f"Falha ao enviar heartbeat: {response.text}")
        except Exception as e:
            print(f"Erro ao enviar heartbeat: {e}")
        time.sleep(60)  # Envia heartbeat a cada 1 minuto

# Rota para construir e executar o container
@app.route('/build_and_run', methods=['POST'])
def build_and_run():
    data = request.get_json()
    image_name = data.get('image_name')
    ports = data.get('ports')
    dockerfile_base64 = data.get('dockerfile_base64')
    name = data.get('name')
    restart_policy = data.get('restart_policy', 'no')

    if not dockerfile_base64:
        return jsonify({"status": "error", "message": "Missing 'dockerfile_base64' in request."}), 400

    # Decode the Dockerfile content
    try:
        dockerfile_content = base64.b64decode(dockerfile_base64).decode('utf-8')
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to decode Dockerfile: {str(e)}"}), 400


    # Criar um diretório temporário para o Dockerfile
    temp_dir = f'/tmp/{image_name}'
    os.makedirs(temp_dir, exist_ok=True)

    # Escrever o Dockerfile no diretório temporário
    dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    try:
        # Construir a imagem Docker a partir do Dockerfile
        image, logs = client.images.build(path=temp_dir, tag=image_name)

        # Iniciar o container com a imagem criada
        container = client.containers.run(
            image_name,
            detach=True,
            ports=ports,
            name=name,
            tty=True,
            restart_policy={"Name": restart_policy},
            labels={"honeypot": "true"}
        )
        return jsonify({"status": "success", "container_id": container.id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        # Remover o diretório temporário após a execução
        if os.path.exists(temp_dir):
            subprocess.call(['rm', '-rf', temp_dir])

# Rota para listar containers relacionados ao honeypot
@app.route('/list_containers', methods=['GET'])
def list_containers():
    try:
        containers = client.containers.list(all=True, filters={"label": "honeypot=true"})
        container_list = []
        for container in containers:
            container_info = {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags
            }
            container_list.append(container_info)
        return jsonify({"status": "success", "containers": container_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para parar e remover container
@app.route('/remove_container', methods=['POST'])
def remove_container():
    data = request.get_json()
    container_name = data.get('container_name')
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        return jsonify({"status": "success", "message": f"Container {container_name} removido."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para autodestruição do agente e dos honeypots criados
@app.route('/self_destruct', methods=['POST'])
def self_destruct():
    try:
        # Parar e remover todos os containers relacionados ao honeypot
        containers = client.containers.list(all=True, filters={"label": "honeypot=true"})
        for container in containers:
            container.stop()
            container.remove()
        # Encerrar o processo do agente
        shutdown_agent()
        return jsonify({"status": "success", "message": "Agente autodestruído com sucesso."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def shutdown_agent():
    # Função para encerrar o servidor Flask
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    else:
        os._exit(0)

# Rota para verificar o status do agente
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Agent is running"}), 200

if __name__ == '__main__':
    # Registrar o agente no controlador
    register_agent()

    # Iniciar thread para enviar heartbeat
    heartbeat_thread = threading.Thread(target=send_heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=agent_port)
