# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema, baixar o agente.py do GitHub, e instalar pacotes Python em uma única layer
RUN apt-get update && \
    apt-get install -y curl && \
    curl -o agent.py https://raw.githubusercontent.com/c1berc0n/honeypot/refs/heads/main/container/agente.py && \
    pip install flask docker requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expor a porta em que o agente irá escutar
EXPOSE 5000

# Comando para executar o agente
CMD ["python", "agent.py"]
