import os
import platform
import socket
import requests
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

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
    try:
        response = requests.post(registration_url, json=data)
        if response.status_code == 200:
            print("Agente registrado com sucesso no controlador.")
        else:
            print(f"Falha ao registrar agente: {response.text}")
    except Exception as e:
        print(f"Erro ao conectar ao controlador: {e}")

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

# Rota para criar container 
@app.route('/create_container', methods=['POST'])
def create_container():
    # Implementação específica para criar containers
    # Deve ser adaptada para Windows e Linux se necessário
    return jsonify({"status": "success", "message": "Operação de criação de container não implementada."}), 200

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
