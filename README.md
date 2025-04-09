# Dashboard de Análise de Serviços de Lavanderia

Este dashboard foi desenvolvido para análise de dados de serviços de lavanderia, permitindo visualizar a quantidade de peças lavadas por cliente, por hora, por tipo de serviço e outros cruzamentos importantes. O sistema inclui autenticação de usuários e gerenciamento de configurações.

## Funcionalidades

O dashboard oferece as seguintes funcionalidades:
- Sistema de login com autenticação de usuários
- Página de configurações para administradores
- Visualização da quantidade de peças processadas por cliente (máquina)
- Análise de dados por hora do dia
- Filtros por período, cliente e horário
- Visualização de tendências ao longo do tempo
- Métricas principais: total processado, horas de operação e média diária
- Download automático do banco de dados do Google Drive

## Credenciais de Acesso

O sistema vem pré-configurado com um usuário administrador:
- Email: ddt@ddt.com.br
- Senha: Tiburcio50

## Requisitos

Para executar o dashboard, você precisa ter Python 3.7+ instalado e as seguintes bibliotecas:

```
dash==2.15.0
dash-bootstrap-components==2.0.0
pandas==2.1.3
plotly==5.18.0
numpy==1.26.2
flask-login==0.6.3
gdown==5.1.0
gunicorn==21.2.0
```

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Navegue até o diretório do projeto
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração do Banco de Dados

O dashboard está configurado para baixar automaticamente o banco de dados SQLite do Google Drive. A configuração é feita através do arquivo `app.py`:

```python
# ID do arquivo no Google Drive
GOOGLE_DRIVE_FILE_ID = '1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H'
DOWNLOAD_FREQUENCY = 86400  # 1 dia em segundos
```

Você pode alterar a frequência de download e o ID do arquivo na página de configurações do sistema.

## Execução

Para iniciar o dashboard, execute:

```bash
python app.py
```

O dashboard estará disponível em http://127.0.0.1:8090/ (ou outra porta disponível) no seu navegador.

## Estrutura do Projeto

- `app.py`: Arquivo principal com a aplicação Dash
- `login.py`: Sistema de autenticação de usuários
- `settings.py`: Página de configurações do sistema
- `users.py`: Gerenciamento de usuários
- `config.py`: Configurações do sistema
- `requirements.txt`: Lista de dependências
- `README.md`: Documentação do projeto

## Funcionalidades do Sistema de Login

O sistema de login implementa:
- Autenticação de usuários com email e senha
- Controle de acesso baseado em permissões (administrador/usuário)
- Página de configurações restrita a administradores
- Gerenciamento de usuários (adicionar, editar, excluir)
- Armazenamento seguro de senhas
