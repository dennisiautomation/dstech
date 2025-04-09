# Guia de Deploy - Dashboard de Lavanderia

Este documento descreve o processo de deploy do Dashboard de Lavanderia para um servidor VPS e a configuração do domínio com HTTPS.

## Pré-requisitos

- Servidor VPS com Ubuntu 24.04 (ou similar)
- Acesso SSH como root
- Domínio configurado para apontar para o IP do servidor
- Python 3.12+ instalado no servidor

## Configuração do Ambiente

### 1. Configuração SSH

Adicione a configuração do servidor no arquivo `~/.ssh/config`:

```
Host vps-dashboard
    HostName 69.62.88.99
    User root
    IdentityFile ~/.ssh/id_ed25519
```

### 2. Dependências do Projeto

O arquivo `requirements.txt` foi atualizado para incluir todas as dependências necessárias:

```
dash==3.0.1
dash-bootstrap-components==2.0.0
dash-bootstrap-templates==1.1.1
pandas==2.1.3
plotly==5.18.0
numpy==1.26.2
flask-login==0.6.3
gdown==5.1.0
gunicorn==21.2.0
```

### 3. Script de Deploy

O script `deploy.sh` automatiza o processo de deploy para o servidor:

```bash
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
StandardOutput=journal
StandardError=journal
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
```

## Configuração do Domínio e HTTPS

### 1. Instalação do Nginx e Certbot

```bash
ssh root@69.62.88.99 "apt-get update && apt-get install -y nginx certbot python3-certbot-nginx"
```

### 2. Configuração do Nginx

Crie um arquivo de configuração para o domínio:

```bash
ssh root@69.62.88.99 "cat > /etc/nginx/sites-available/dstech.iautomation.com.br << 'EOL'
server {
    listen 80;
    server_name dstech.iautomation.com.br;

    location / {
        proxy_pass http://localhost:8090;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL"
```

### 3. Ativação do Site e Certificado SSL

```bash
# Ativar o site
ssh root@69.62.88.99 "ln -s /etc/nginx/sites-available/dstech.iautomation.com.br /etc/nginx/sites-enabled/ && nginx -t && systemctl restart nginx"

# Obter certificado SSL
ssh root@69.62.88.99 "certbot --nginx -d dstech.iautomation.com.br --non-interactive --agree-tos --email ddt@ddt.com.br"
```

## Acesso ao Dashboard

O dashboard está disponível em:
- URL: https://dstech.iautomation.com.br
- Credenciais de administrador:
  - Email: ddt@ddt.com.br
  - Senha: Tiburcio50

## Manutenção

### Atualização do Código

Para atualizar o código no servidor, basta executar novamente o script `deploy.sh`.

### Renovação do Certificado SSL

O certificado SSL é renovado automaticamente pelo Certbot.

### Logs do Sistema

Para verificar os logs do dashboard:
```bash
ssh root@69.62.88.99 "journalctl -u dashboard-lavanderia.service -n 50"
```

Para verificar os logs do Nginx:
```bash
ssh root@69.62.88.99 "journalctl -u nginx.service -n 50"
```
