from flask import Flask, request, jsonify
import threading
import time

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
            else:
                print(f"Agente {agent_name} está online.")
        time.sleep(60)  # Verifica a cada 1 minuto

if __name__ == '__main__':
    # Iniciar thread para monitorar agentes
    monitor_thread = threading.Thread(target=monitor_agents)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=5050)
