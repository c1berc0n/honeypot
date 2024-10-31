import threading
import time
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dicionário para armazenar os agentes registrados
registered_agents = {}

# Rota para registrar o agente
@app.route('/register_agent', methods=['POST'])
def register_agent():
    data = request.get_json()
    agent_name = data.get('agent_name')
    agent_info = {
        "agent_ip": data.get('agent_ip'),
        "agent_port": data.get('agent_port'),
        "agent_os": data.get('agent_os'),
        "last_seen": time.time()
    }
    registered_agents[agent_name] = agent_info
    print(f"Agente {agent_name} registrado.")
    return jsonify({"status": "success", "message": "Agente registrado com sucesso."}), 200

# Rota para receber heartbeat do agente
@app.route('/agent_heartbeat', methods=['POST'])
def agent_heartbeat():
    data = request.get_json()
    agent_name = data.get('agent_name')
    if agent_name in registered_agents:
        registered_agents[agent_name]['last_seen'] = time.time()
        print(f"Heartbeat recebido de {agent_name}.")
        return jsonify({"status": "success", "message": "Heartbeat recebido."}), 200
    else:
        print(f"Agente {agent_name} não registrado.")
        return jsonify({"status": "error", "message": "Agente não registrado."}), 400

# Função para verificar o status dos agentes
def monitor_agents():
    while True:
        current_time = time.time()
        for agent_name, agent_info in list(registered_agents.items()):
            last_seen = agent_info['last_seen']
            if current_time - last_seen > 120:  # 2 minutos sem heartbeat
                print(f"Agente {agent_name} está offline.")
                registered_agents[agent_name]['status'] = 'offline'
            else:
                print(f"Agente {agent_name} está online.")
                registered_agents[agent_name]['status'] = 'online'
        time.sleep(60)  # Verifica a cada 1 minuto

# Rota para listar agentes registrados
@app.route('/list_agents', methods=['GET'])
def list_agents():
    return jsonify(registered_agents), 200

# Rota para enviar Dockerfile e instruções para o agente construir e executar o container
@app.route('/deploy_container', methods=['POST'])
def deploy_container():
    data = request.get_json()
    agent_name = data.get('agent_name')
    if agent_name not in registered_agents:
        return jsonify({"status": "error", "message": "Agente não registrado."}), 400

    agent_info = registered_agents[agent_name]
    agent_ip = agent_info['agent_ip']
    agent_port = agent_info['agent_port']

    # Dados necessários para o agente
    payload = {
        "image_name": data.get('image_name'),
        "dockerfile_base64": data.get('dockerfile_base64'),  # Opcional
        "use_predefined": data.get('use_predefined', False),
        "ports": data.get('ports'),
        "name": data.get('name'),
        "restart_policy": data.get('restart_policy', 'no')
    }

    try:
        response = requests.post(f'http://{agent_ip}:{agent_port}/build_and_run', json=payload)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para parar e remover container no agente
@app.route('/remove_container', methods=['POST'])
def remove_container():
    data = request.get_json()
    agent_name = data.get('agent_name')
    container_name = data.get('container_name')

    if agent_name not in registered_agents:
        return jsonify({"status": "error", "message": "Agente não registrado."}), 400

    agent_info = registered_agents[agent_name]
    agent_ip = agent_info['agent_ip']
    agent_port = agent_info['agent_port']

    payload = {
        "container_name": container_name
    }

    try:
        response = requests.post(f'http://{agent_ip}:{agent_port}/remove_container', json=payload)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para solicitar autodestruição do agente
@app.route('/destroy_agent', methods=['POST'])
def destroy_agent():
    data = request.get_json()
    agent_name = data.get('agent_name')

    if agent_name not in registered_agents:
        return jsonify({"status": "error", "message": "Agente não registrado."}), 400

    agent_info = registered_agents[agent_name]
    agent_ip = agent_info['agent_ip']
    agent_port = agent_info['agent_port']

    try:
        response = requests.post(f'http://{agent_ip}:{agent_port}/self_destruct')
        if response.status_code == 200:
            # Remover agente da lista de registrados
            del registered_agents[agent_name]
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Iniciar thread para monitorar agentes
    monitor_thread = threading.Thread(target=monitor_agents)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=5050)
