# Configurações do banco de dados

# Tipo de banco de dados (sqlite, mysql, postgresql, sqlserver)
DB_TYPE = 'sqlite'

# Configurações para SQLite
DB_PATH = 'dstechBD.db'  # Nome do arquivo local após download

# URL do Google Drive para download do banco de dados
GOOGLE_DRIVE_URL = 'https://drive.google.com/file/d/1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H/view?usp=sharing'
GOOGLE_DRIVE_FILE_ID = '1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H'  # ID extraído da URL

# Configurações para download do banco de dados
GOOGLE_DRIVE_FILE_ID = '1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H'  # ID do arquivo no Google Drive
DOWNLOAD_FREQUENCY = 86400  # Frequência de download em segundos (1 dia)

# Configuração da frequência de download (em segundos)
# 0 = apenas se o arquivo não existir (nPODE INICIALIão baixa novamente)
# 3600 = a cada hora
# 86400 = a cada dia (24 horas)
# 604800 = a cada semana

# Configurações para MySQL/MariaDB
MYSQL_CONFIG = {
    'host': 'localhost',     # Endereço do servidor
    'port': '3306',          # Porta padrão do MySQL
    'database': 'lavanderia',  # Nome do banco de dados
    'user': 'usuario',       # Nome do usuário
    'password': 'senha'      # Senha do usuário
}

# Configurações para PostgreSQL
POSTGRESQL_CONFIG = {
    'host': 'localhost',     # Endereço do servidor
    'port': '5432',          # Porta padrão do PostgreSQL
    'dbname': 'lavanderia',  # Nome do banco de dados
    'user': 'usuario',       # Nome do usuário
    'password': 'senha'      # Senha do usuário
}

# Configurações para SQL Server Express
SQLSERVER_CONFIG = {
    'server': 'localhost\\SQLEXPRESS',  # Nome do servidor (inclui a instância SQLEXPRESS)
    'database': 'lavanderia',           # Nome do banco de dados
    'user': 'sa',                       # Nome do usuário
    'password': 'senha',                # Senha do usuário
    'driver': 'ODBC Driver 17 for SQL Server',  # Driver ODBC (pode ser necessário ajustar)
    'trusted_connection': 'no'          # Use 'yes' para autenticação do Windows
}

# Nome da tabela e campos específicos (se precisar alterar)
TABLE_NAME = 'DADOS'
DATE_FIELD = 'DATA'
TIME_FIELD = 'HORA'
MACHINE_FIELD = 'MAQUINA'
# Como não existe a coluna CLIENTE, vamos usar a coluna LINHA como substituto
CLIENT_FIELD = 'LINHA'
PIECES_IN_FIELD = 'PECAS_TOT_ENT'
PIECES_OUT_FIELD = 'PECAS_TOT_SAI'
# Como não existem as colunas EFICIENCIA e UTILIZACAO, vamos usar cálculos baseados em outras colunas
# EFICIENCIA será calculada como (EF_ENTRADA + EF_SAIDA) / 2
EFFICIENCY_FIELD_CALC = True  # Indica que o campo precisa ser calculado
EFFICIENCY_FIELD_FORMULA = ['EF_ENTRADA', 'EF_SAIDA']  # Campos usados no cálculo
# UTILIZACAO será calculada como TEMPO_MAQ_LIGADA / (TEMPO_MAQ_LIGADA + TEMPO_MAQ_PARADA) * 100
UTILIZATION_FIELD_CALC = True  # Indica que o campo precisa ser calculado
UTILIZATION_FIELD_FORMULA = ['TEMPO_MAQ_LIGADA', 'TEMPO_MAQ_PARADA']  # Campos usados no cálculo
