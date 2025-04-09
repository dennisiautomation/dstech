#!/bin/bash

# Script de deploy para o Dashboard de Lavanderia
echo "Iniciando deploy do Dashboard de Lavanderia..."

# Criar diretório remoto se não existir
ssh root@69.62.88.99 "mkdir -p /var/www/dashboard_lavanderia"

# Enviar arquivos para o servidor
echo "Enviando arquivos para o servidor..."
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' --exclude 'venv' --exclude '*.db' ./ root@69.62.88.99:/var/www/dashboard_lavanderia/

# Instalar dependências no servidor usando ambiente virtual
echo "Instalando dependências no servidor usando ambiente virtual..."
ssh root@69.62.88.99 "cd /var/www/dashboard_lavanderia && \
    apt-get install -y python3-full python3-venv && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt"

# Configurar serviço systemd para manter o aplicativo rodando
echo "Configurando serviço systemd..."
ssh root@69.62.88.99 "cat > /etc/systemd/system/dashboard-lavanderia.service << 'EOL'
[Unit]
Description=Dashboard Lavanderia
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/dashboard_lavanderia
ExecStart=/var/www/dashboard_lavanderia/venv/bin/python /var/www/dashboard_lavanderia/app.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=dashboard-lavanderia
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL"

# Recarregar systemd, habilitar e iniciar o serviço
echo "Iniciando o serviço..."
ssh root@69.62.88.99 "systemctl daemon-reload && systemctl enable dashboard-lavanderia.service && systemctl restart dashboard-lavanderia.service"

# Verificar status do serviço
echo "Verificando status do serviço..."
ssh root@69.62.88.99 "systemctl status dashboard-lavanderia.service"

echo "Deploy concluído! O dashboard está disponível em http://69.62.88.99:8090/"
