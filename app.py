# Imports
import os
import sqlite3
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import gdown
import time
import traceback
import socket
from dash_bootstrap_templates import load_figure_template
from flask_login import LoginManager, current_user, login_required
from users import User, get_user, get_users, get_user_by_email, add_user, edit_user, delete_user
from login import create_login_layout, validate_login, create_logout
from settings import create_settings_layout

# Carregar template para os gráficos
load_figure_template("bootstrap")

# Configuração do aplicativo
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

# Configurar o servidor Flask para login
server = app.server
server.secret_key = 'uma_chave_secreta_muito_segura_para_o_dashboard'

# Configurar o gerenciador de login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

# Layout do aplicativo
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='auth-store', storage_type='session'),
    dcc.Store(id='initialization-store', data=str(datetime.now()))
])

# Layout da página de login
def create_login_layout():
    return html.Div([
        html.Div([
            html.Img(src='/assets/logo.png', style={'height': '180px', 'margin-bottom': '30px'}),
            html.H2("Login do Sistema", className="mb-4", style={'color': '#2c3e50', 'font-weight': '700'}),
            html.Div(id="login-error", style={'color': 'red', 'margin-bottom': '15px'}),
            html.Div([
                html.Label("Email", htmlFor="login-email", className="form-label"),
                dbc.Input(
                    type="email",
                    id="login-email",
                    placeholder="Digite seu email",
                    className="mb-3"
                ),
            ], className="mb-3"),
            html.Div([
                html.Label("Senha", htmlFor="login-password", className="form-label"),
                dbc.Input(
                    type="password",
                    id="login-password",
                    placeholder="Digite sua senha",
                    className="mb-3"
                ),
            ], className="mb-3"),
            dbc.Button(
                "Entrar",
                id="login-button",
                color="primary",
                className="mt-3 w-100",
                n_clicks=0
            ),
        ], style={
            'width': '400px',
            'margin': '100px auto',
            'padding': '30px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'borderRadius': '8px',
            'backgroundColor': 'white',
            'textAlign': 'center'
        }),
    ])

# Callback para roteamento de páginas
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('auth-store', 'data')]
)
def display_page(pathname, auth_data):
    if pathname == '/logout':
        return create_login_layout()
    
    if pathname == '/settings' and auth_data and auth_data.get('authenticated'):
        return create_settings_layout()
    
    if auth_data and auth_data.get('authenticated'):
        return create_dashboard_layout()
    else:
        return create_login_layout()

# Callback para autenticação
@app.callback(
    [Output('auth-store', 'data'),
     Output('login-error', 'children'),
     Output('url', 'pathname')],
    [Input('login-button', 'n_clicks')],
    [State('login-email', 'value'),
     State('login-password', 'value')]
)
def login_callback(n_clicks, email, password):
    if n_clicks is None or n_clicks == 0:
        # Inicialização, não fazer nada
        return None, "", "/"
    
    if email == "ddt@ddt.com.br" and password == "Tiburcio50":
        return {'authenticated': True, 'is_admin': True, 'username': 'ddt'}, "", "/"
    else:
        return None, "Email ou senha incorretos. Tente novamente.", "/"

# Layout da página de configurações
def create_settings_layout():
    return html.Div([
        # Cabeçalho
        html.H2("Configurações do Sistema", className="mb-4"),
        
        # Seção de gerenciamento de usuários
        dbc.Card([
            dbc.CardHeader("Gerenciamento de Usuários"),
            dbc.CardBody([
                html.H5("Usuário Administrador", className="mb-3"),
                dbc.ListGroup([
                    dbc.ListGroupItem([
                        html.Div([
                            html.Strong("Nome: "), "Administrador"
                        ], className="d-flex justify-content-between"),
                        html.Div([
                            html.Strong("Email: "), "ddt@ddt.com.br"
                        ], className="d-flex justify-content-between mt-2"),
                        html.Div([
                            html.Strong("Tipo: "), 
                            dbc.Badge("Administrador", color="primary")
                        ], className="d-flex justify-content-between mt-2")
                    ])
                ], className="mb-4"),
                
                html.H5("Adicionar Novo Usuário", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Nome de Usuário"),
                        dbc.Input(id="new-username", type="text", placeholder="Digite o nome de usuário")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Email"),
                        dbc.Input(id="new-email", type="email", placeholder="Digite o email")
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Senha"),
                        dbc.Input(id="new-password", type="password", placeholder="Digite a senha")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Confirmar Senha"),
                        dbc.Input(id="confirm-password", type="password", placeholder="Confirme a senha")
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Checkbox(
                            id="new-is-admin",
                            label="Usuário Administrador",
                            value=False
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Button("Adicionar Usuário", id="add-user-button", color="success", className="float-end")
                    ], width=6, className="d-flex justify-content-end")
                ]),
                
                html.Div(id="user-feedback", className="mt-3")
            ])
        ], className="mb-4"),
        
        # Seção de configurações do sistema
        dbc.Card([
            dbc.CardHeader("Configurações do Sistema"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Frequência de Download do Banco de Dados (dias)"),
                        dbc.Input(id="download-frequency", type="number", value=1, min=1, max=30)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("ID do Arquivo no Google Drive"),
                        dbc.Input(id="google-drive-id", type="text", value="1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H")
                    ], width=6)
                ], className="mb-3"),
                dbc.Button("Salvar Configurações", id="save-config-button", color="primary", className="mt-3")
            ])
        ], className="mb-4"),
        
        # Botão para voltar ao dashboard
        dbc.Button("Voltar ao Dashboard", href="/", color="secondary", className="mt-4")
    ], className="p-4")

# Estilos CSS personalizados
styles = {
    'body': {
        'font-family': "'Roboto', 'Helvetica Neue', Arial, sans-serif",
        'background-color': '#f5f7fa',
        'margin': '0',
        'padding': '20px',
        'color': '#2c3e50'
    },
    'header': {
        'color': '#2c3e50',
        'font-weight': '700',
        'margin-bottom': '30px',
        'border-bottom': '3px solid #3498db',
        'padding-bottom': '15px',
        'text-align': 'center',
        'font-size': '2.2rem',
        'text-shadow': '1px 1px 3px rgba(0,0,0,0.2)'
    },
    'filters_container': {
        'display': 'flex',
        'flex-wrap': 'wrap',
        'gap': '20px',
        'background-color': 'white',
        'padding': '25px',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0, 0, 0, 0.08)',
        'margin-bottom': '25px',
        'border-left': '5px solid #3498db'
    },
    'filter_item': {
        'flex': '1 1 220px'
    },
    'filter_label': {
        'font-weight': '600',
        'color': '#2c3e50',
        'margin-bottom': '8px',
        'display': 'block'
    },
    'kpi_container': {
        'display': 'flex',
        'flex-wrap': 'wrap',
        'gap': '20px',
        'margin-bottom': '25px'
    },
    'kpi_card': {
        'flex': '1 1 220px',
        'background': 'linear-gradient(135deg, #ffffff 0%, #e6f7ff 100%)',
        'padding': '25px',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0, 0, 0, 0.08)',
        'text-align': 'center',
        'border-top': '5px solid #3498db'
    },
    'kpi_value': {
        'font-size': '2.5rem',
        'font-weight': '700',
        'color': '#3498db',
        'margin': '0'
    },
    'kpi_label': {
        'color': '#7f8c8d',
        'margin-top': '10px',
        'font-weight': '500',
        'font-size': '1.1rem'
    },
    'charts_container': {
        'display': 'flex',
        'flex-wrap': 'wrap',
        'gap': '25px',
        'margin-bottom': '25px'
    },
    'chart_card': {
        'flex': '1 1 calc(50% - 25px)',
        'min-width': '350px',
        'background-color': 'white',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0, 0, 0, 0.08)',
        'padding': '20px',
        'border-top': '4px solid #3498db'
    },
    'chart_card_wide': {
        'flex': '1 1 100%',
        'background-color': 'white',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0, 0, 0, 0.08)',
        'padding': '20px',
        'margin-bottom': '25px',
        'border-top': '4px solid #3498db'
    },
    'table_container': {
        'background-color': 'white',
        'border-radius': '12px',
        'box-shadow': '0 4px 15px rgba(0, 0, 0, 0.08)',
        'padding': '25px',
        'margin-bottom': '25px',
        'border-left': '5px solid #3498db'
    },
    'data_table': {
        'overflow-x': 'auto'
    },
    'subtitle': {
        'color': '#7f8c8d', 
        'text-align': 'center', 
        'margin-top': '-15px', 
        'margin-bottom': '25px',
        'font-size': '1.1rem'
    },
    'card_title': {
        'color': '#3498db',
        'font-weight': '600',
        'font-size': '1.2rem',
        'margin-bottom': '15px',
        'display': 'flex',
        'align-items': 'center',
        'gap': '10px'
    },
    'icon': {
        'margin-right': '8px',
        'color': '#3498db'
    }
}

# Configurações do banco de dados
DB_PATH = 'dstechBD.db'
TABLE_NAME = 'DADOS'
DATE_FIELD = 'DATA'
MACHINE_FIELD = 'MAQUINA'
CLIENT_FIELD = 'LINHA'
PIECES_IN_FIELD = 'PECAS_TOT_ENT'
PIECES_OUT_FIELD = 'PECAS_TOT_SAI'
EFFICIENCY_IN_FIELD = 'EF_ENTRADA'
EFFICIENCY_OUT_FIELD = 'EF_SAIDA'
OPERATION_TIME_FIELD = 'TEMPO_MAQ_LIGADA'
IDLE_TIME_FIELD = 'TEMPO_MAQ_PARADA'

# ID do arquivo no Google Drive
GOOGLE_DRIVE_FILE_ID = '1vuJE0AxKhRrdt6gtKQnhp6pbviJvYt2H'
DOWNLOAD_FREQUENCY = 86400  # 1 dia em segundos

# Função para baixar o banco de dados do Google Drive
def download_database():
    """Baixa o banco de dados do Google Drive"""
    try:
        print("Verificando banco de dados...")
        
        # Verificar se o arquivo já existe e se precisa ser baixado novamente
        if os.path.exists(DB_PATH):
            # Verificar a idade do arquivo
            file_age = time.time() - os.path.getmtime(DB_PATH)
            
            if file_age < DOWNLOAD_FREQUENCY:
                print(f"Usando banco de dados existente: {DB_PATH}")
                
                # Verificar integridade do banco
                if verify_database_integrity():
                    return True
                else:
                    print("Banco de dados corrompido. Baixando novamente...")
            else:
                print(f"Banco de dados desatualizado. Baixando novamente...")
        else:
            print("Banco de dados não encontrado. Baixando...")
        
        # Instalar gdown se necessário
        try:
            import gdown
            print("Biblioteca gdown já está instalada.")
        except ImportError:
            print("Instalando biblioteca gdown...")
            os.system("pip install gdown")
            import gdown
        
        # Baixar o arquivo
        output = DB_PATH
        url = f'https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}'
        gdown.download(url, output, quiet=False)
        
        # Verificar se o download foi bem-sucedido
        if os.path.exists(DB_PATH):
            if verify_database_integrity():
                print(f"Banco de dados baixado com sucesso: {DB_PATH}")
                return True
            else:
                print("Erro: O arquivo baixado não é um banco de dados SQLite válido.")
                return False
        else:
            print("Erro ao baixar o banco de dados.")
            return False
    
    except Exception as e:
        print(f"Erro ao baixar o banco de dados: {str(e)}")
        return False

# Função para verificar a integridade do banco de dados
def verify_database_integrity():
    """Verifica se o arquivo é um banco de dados SQLite válido"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela DADOS existe
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='DADOS'")
        if cursor.fetchone()[0] == 0:
            conn.close()
            return False
        
        # Verificar se há registros na tabela
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        print(f"Total de registros na tabela DADOS: {count}")
        
        conn.close()
        print("Verificação de integridade do banco de dados: OK")
        return True
    
    except Exception as e:
        print(f"Erro ao verificar integridade do banco de dados: {str(e)}")
        return False

# Layout do dashboard
def create_dashboard_layout():
    """Cria o layout do dashboard"""
    return html.Div([
        # Cabeçalho
        html.Div([
            html.Div([
                html.Img(src='/assets/logo.png', style={'height': '180px', 'margin-right': '30px'}),
                html.Div([
                    html.H1("Dashboard de Monitoramento de Lavanderia", 
                           style={'color': '#2c3e50', 'font-weight': '700', 'margin-bottom': '15px', 'font-size': '2.2rem', 'text-shadow': '1px 1px 3px rgba(0,0,0,0.2)'}),
                    html.P("Monitoramento em tempo real de máquinas e produção", 
                          style={'color': '#7f8c8d', 'margin-top': '0', 'font-size': '1.2rem'})
                ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'})
            ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '30px', 'border-bottom': '3px solid #3498db', 'padding-bottom': '20px'})
        ], className='header-container'),
        
        # Barra superior com usuário e botões
        html.Div([
            html.Div([
                html.Span("Usuário: Admin", className="me-3", style={'font-weight': 'bold'}),
                dbc.Button("Sair", href="/logout", color="danger", size="sm", className="me-2"),
                dbc.Button("Configurações", href="/settings", color="secondary", size="sm")
            ], style={'display': 'flex', 'justify-content': 'flex-end', 'align-items': 'center', 'margin-bottom': '20px'})
        ]),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label("Período de Análise", style=styles['filter_label']),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date_placeholder_text="Data Inicial",
                    end_date_placeholder_text="Data Final",
                    calendar_orientation='horizontal',
                    start_date=(datetime.now() - timedelta(days=30)).date(),
                    end_date=datetime.now().date(),
                    display_format='DD/MM/YYYY'
                )
            ], style=styles['filter_item'], className='filter-item'),
            
            html.Div([
                html.Label("Máquina", style=styles['filter_label']),
                dcc.Dropdown(
                    id='machine-dropdown',
                    options=[
                        {'label': 'Todas', 'value': 'all'},
                        {'label': 'Máquina 1', 'value': '1'},
                        {'label': 'Máquina 2', 'value': '2'},
                        {'label': 'Máquina 3', 'value': '3'}
                    ],
                    value='all',
                    clearable=False
                )
            ], style=styles['filter_item'], className='filter-item'),
            
            html.Div([
                html.Label("Cliente", style=styles['filter_label']),
                dcc.Dropdown(
                    id='client-dropdown',
                    options=[
                        {'label': 'Todos', 'value': 'all'},
                        {'label': 'Cliente 1', 'value': '1'}
                    ],
                    value='all',
                    clearable=False
                )
            ], style=styles['filter_item'], className='filter-item'),
            
            html.Div([
                html.Label("Eficiência", style=styles['filter_label']),
                dcc.Dropdown(
                    id='efficiency-dropdown',
                    options=[
                        {'label': 'Todos', 'value': 'all'},
                        {'label': 'Alta (>80%)', 'value': 'high'},
                        {'label': 'Média (50-80%)', 'value': 'medium'},
                        {'label': 'Baixa (<50%)', 'value': 'low'}
                    ],
                    value='all',
                    clearable=False
                )
            ], style=styles['filter_item'], className='filter-item'),
            
            html.Div([
                html.Label("Utilização", style=styles['filter_label']),
                dcc.Dropdown(
                    id='utilization-dropdown',
                    options=[
                        {'label': 'Todos', 'value': 'all'},
                        {'label': 'Alta (>80%)', 'value': 'high'},
                        {'label': 'Média (50-80%)', 'value': 'medium'},
                        {'label': 'Baixa (<50%)', 'value': 'low'}
                    ],
                    value='all',
                    clearable=False
                )
            ], style=styles['filter_item'], className='filter-item')
        ], style=styles['filters_container']),
        
        # KPIs
        html.Div([
            html.Div([
                html.H3(id='kpi-total-pieces', children="0", style=styles['kpi_value']),
                html.P("Total de Peças", style=styles['kpi_label'])
            ], style=styles['kpi_card'], className='kpi-card'),
            
            html.Div([
                html.H3(id='kpi-daily-avg', children="0", style=styles['kpi_value']),
                html.P("Média Diária", style=styles['kpi_label'])
            ], style=styles['kpi_card'], className='kpi-card'),
            
            html.Div([
                html.H3(id='kpi-pieces-in', children="0", style=styles['kpi_value']),
                html.P("Peças Entrada", style=styles['kpi_label'])
            ], style=styles['kpi_card'], className='kpi-card'),
            
            html.Div([
                html.H3(id='kpi-pieces-out', children="0", style=styles['kpi_value']),
                html.P("Peças Saída", style=styles['kpi_label'])
            ], style=styles['kpi_card'], className='kpi-card')
        ], style=styles['kpi_container']),
        
        # Gráficos
        html.Div([
            html.Div([
                html.H4("Produção por Máquina", style=styles['card_title']),
                dcc.Graph(id='bar-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card'),
            
            html.Div([
                html.H4("Tendência de Produção", style=styles['card_title']),
                dcc.Graph(id='line-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card'),
            
            html.Div([
                html.H4("Distribuição por Cliente", style=styles['card_title']),
                dcc.Graph(id='pie-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card'),
            
            html.Div([
                html.H4("Comparação: Entrada vs Saída", style=styles['card_title']),
                dcc.Graph(id='comparison-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card')
        ], style=styles['charts_container']),
        
        # Gráficos adicionais
        html.Div([
            html.H4("Produção por Dia e Hora", style=styles['card_title']),
            dcc.Graph(id='heatmap-chart', config={'displayModeBar': False})
        ], style=styles['chart_card_wide'], className='chart-card'),
        
        html.Div([
            html.Div([
                html.H4("Eficiência por Máquina", style=styles['card_title']),
                dcc.Graph(id='efficiency-comparison-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card'),
            
            html.Div([
                html.H4("Tendência de Utilização", style=styles['card_title']),
                dcc.Graph(id='utilization-trend-chart', config={'displayModeBar': False})
            ], style=styles['chart_card'], className='chart-card')
        ], style=styles['charts_container']),
        
        html.Div([
            html.H4("Desempenho por Cliente", style=styles['card_title']),
            dcc.Graph(id='client-performance-chart', config={'displayModeBar': False})
        ], style=styles['chart_card_wide'], className='chart-card'),
        
        # Tabela de dados
        html.Div([
            html.H4("Dados Detalhados", style=styles['card_title']),
            html.Div(id='data-table', style=styles['data_table'])
        ], style=styles['table_container']),
        
        # Store para armazenar o estado dos filtros
        dcc.Store(id='filter-store'),
    ], style=styles['body'])

# Callback para atualizar todos os gráficos e KPIs
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('comparison-chart', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('kpi-total-pieces', 'children'),
     Output('kpi-daily-avg', 'children'),
     Output('kpi-pieces-in', 'children'),
     Output('kpi-pieces-out', 'children'),
     Output('data-table', 'children'),
     Output('efficiency-comparison-chart', 'figure'),
     Output('utilization-trend-chart', 'figure'),
     Output('client-performance-chart', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('machine-dropdown', 'value'),
     Input('client-dropdown', 'value'),
     Input('initialization-store', 'data')]
)
def update_dashboard(start_date, end_date, selected_machines, selected_clients, _):
    """Atualiza os gráficos e KPIs com base nos filtros selecionados"""
    print("\n" + "="*80)
    print("ATUALIZANDO GRÁFICOS")
    print("="*80)
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        
        # Construir a consulta SQL base
        query = f"SELECT * FROM {TABLE_NAME}"
        
        # Adicionar filtros
        conditions = []
        
        if start_date and end_date:
            conditions.append(f"{DATE_FIELD} BETWEEN '{start_date}' AND '{end_date}'")
        
        if selected_machines and selected_machines != 'all':
            conditions.append(f"{MACHINE_FIELD} = {selected_machines}")
        
        if selected_clients and selected_clients != 'all':
            conditions.append(f"{CLIENT_FIELD} = {selected_clients}")
        
        # Adicionar condições à consulta
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Executar a consulta
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Verificar se há dados
        if df.empty:
            return empty_charts()
        
        # Converter a coluna de data para datetime
        df['DATA'] = pd.to_datetime(df['DATA'])
        
        # Calcular métricas adicionais
        df['UTILIZACAO'] = df[OPERATION_TIME_FIELD] / (df[OPERATION_TIME_FIELD] + df[IDLE_TIME_FIELD]) * 100
        
        # Aplicar filtros de eficiência e utilização
        if 'high' in df.columns:
            df = df[df['high'] > 80]
        elif 'medium' in df.columns:
            df = df[(df['medium'] >= 50) & (df['medium'] <= 80)]
        elif 'low' in df.columns:
            df = df[df['low'] < 50]
        
        # Verificar novamente se há dados após os filtros
        if df.empty:
            return empty_charts()
        
        # Calcular KPIs
        total_pecas = df[PIECES_IN_FIELD].sum()
        pecas_entrada = df[PIECES_IN_FIELD].sum()
        pecas_saida = df[PIECES_OUT_FIELD].sum()
        dias_unicos = df['DATA'].dt.date.nunique()
        media_diaria = total_pecas / max(dias_unicos, 1)  # Evitar divisão por zero
        
        # Configuração de tema claro para todos os gráficos
        light_template = dict(
            layout=dict(
                paper_bgcolor='#f5f7fa',
                plot_bgcolor='#f5f7fa',
                font=dict(color='#2c3e50'),
                title=dict(font=dict(color='#3498db', size=18)),
                xaxis=dict(
                    gridcolor='#cccccc',
                    zerolinecolor='#cccccc',
                    title=dict(font=dict(color='#2c3e50')),
                    tickfont=dict(color='#2c3e50')
                ),
                yaxis=dict(
                    gridcolor='#cccccc',
                    zerolinecolor='#cccccc',
                    title=dict(font=dict(color='#2c3e50')),
                    tickfont=dict(color='#2c3e50')
                ),
                legend=dict(font=dict(color='#2c3e50')),
                margin=dict(t=50, b=50, l=50, r=30)
            )
        )
        
        # 1. Gráfico de barras - Produção por máquina
        bar_fig = px.bar(
            df.groupby(MACHINE_FIELD)[PIECES_IN_FIELD].sum().reset_index(),
            x=MACHINE_FIELD, y=PIECES_IN_FIELD,
            title='Produção por Máquina',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        bar_fig.update_layout(**light_template['layout'])
        
        # 2. Gráfico de linha - Tendência de produção
        line_data = df.groupby(df['DATA'].dt.date)[PIECES_IN_FIELD].sum().reset_index()
        line_fig = px.line(
            line_data,
            x='DATA', y=PIECES_IN_FIELD,
            title='Tendência de Produção',
            line_shape='spline',
            color_discrete_sequence=['#3498db']
        )
        line_fig.update_layout(**light_template['layout'])
        
        # 3. Gráfico de pizza - Distribuição por cliente
        # Verificar se há mais de um cliente antes de criar o gráfico de pizza
        client_data = df.groupby(CLIENT_FIELD)[PIECES_IN_FIELD].sum().reset_index()
        
        if len(client_data) > 1:
            pie_fig = px.pie(
                client_data,
                values=PIECES_IN_FIELD,
                names=CLIENT_FIELD,
                title='Distribuição por Cliente',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
        else:
            # Se houver apenas um cliente, criar um gráfico de barras horizontal
            pie_fig = px.bar(
                client_data,
                y=CLIENT_FIELD,
                x=PIECES_IN_FIELD,
                title='Produção do Cliente',
                orientation='h',
                color_discrete_sequence=['#3498db']
            )
            pie_fig.update_layout(yaxis_title='Cliente')
            
        pie_fig.update_layout(**light_template['layout'])
        pie_fig.update_traces(textfont_color='#2c3e50')
        
        # 4. Gráfico de comparação - Entrada vs Saída
        comparison_data = pd.DataFrame({
            'Tipo': ['Entrada', 'Saída'],
            'Peças': [pecas_entrada, pecas_saida]
        })
        comparison_fig = px.bar(
            comparison_data,
            x='Tipo',
            y='Peças',
            title='Comparação: Entrada vs Saída',
            color='Tipo',
            color_discrete_map={'Entrada': '#3498db', 'Saída': '#2ecc71'}
        )
        comparison_fig.update_layout(**light_template['layout'])
        
        # Adicionar comparação de eficiência entrada vs saída
        efficiency_comparison_data = pd.DataFrame({
            'Tipo': ['Eficiência Entrada', 'Eficiência Saída'],
            'Valor (%)': [df[EFFICIENCY_IN_FIELD].mean(), df[EFFICIENCY_OUT_FIELD].mean()]
        })
        efficiency_fig = px.bar(
            efficiency_comparison_data,
            x='Tipo',
            y='Valor (%)',
            title='Comparação de Eficiência',
            color='Tipo',
            color_discrete_map={'Eficiência Entrada': '#e74c3c', 'Eficiência Saída': '#9b59b6'}
        )
        efficiency_fig.update_layout(**light_template['layout'])
        
        # Comparação de utilização por máquina
        utilization_by_machine = df.groupby(MACHINE_FIELD)['UTILIZACAO'].mean().reset_index()
        utilization_fig = px.bar(
            utilization_by_machine,
            x=MACHINE_FIELD,
            y='UTILIZACAO',
            title='Utilização por Máquina (%)',
            color_discrete_sequence=['#9b59b6']
        )
        utilization_fig.update_layout(**light_template['layout'])
        
        # Comparação de desempenho por cliente
        client_fig = px.bar(
            df.groupby(CLIENT_FIELD)[PIECES_IN_FIELD].sum().reset_index(),
            x=CLIENT_FIELD,
            y=PIECES_IN_FIELD,
            title='Desempenho por Cliente',
            color_discrete_sequence=['#f39c12']
        )
        client_fig.update_layout(**light_template['layout'])
        
        # 5. Mapa de calor - Produção por dia e hora
        df['DiaSemana'] = df['DATA'].dt.day_name()
        df['Hora'] = df['DATA'].dt.hour
        heatmap_data = df.groupby(['DiaSemana', 'Hora'])[PIECES_IN_FIELD].sum().reset_index()
        heatmap_fig = px.density_heatmap(
            heatmap_data,
            x='Hora',
            y='DiaSemana',
            z=PIECES_IN_FIELD,
            title='Produção por Dia e Hora',
            color_continuous_scale='Blues'
        )
        heatmap_fig.update_layout(**light_template['layout'])
        
        # 6. Gráfico de eficiência por máquina
        efficiency_comparison_fig = px.bar(
            df.groupby(MACHINE_FIELD)[EFFICIENCY_IN_FIELD].mean().reset_index(),
            x=MACHINE_FIELD, y=EFFICIENCY_IN_FIELD,
            title='Eficiência por Máquina',
            color_discrete_sequence=['#e74c3c']
        )
        efficiency_comparison_fig.update_layout(**light_template['layout'])
        
        # 7. Gráfico de tendência de utilização
        utilization_trend_data = df.groupby(df['DATA'].dt.date)['UTILIZACAO'].mean().reset_index()
        utilization_trend_fig = px.line(
            utilization_trend_data,
            x='DATA', y='UTILIZACAO',
            title='Tendência de Utilização',
            line_shape='spline',
            color_discrete_sequence=['#9b59b6']
        )
        utilization_trend_fig.update_layout(**light_template['layout'])
        
        # 8. Gráfico de desempenho por cliente
        client_performance_fig = px.bar(
            df.groupby(CLIENT_FIELD)[PIECES_IN_FIELD].sum().reset_index(),
            x=CLIENT_FIELD, y=PIECES_IN_FIELD,
            title='Desempenho por Cliente',
            color_discrete_sequence=['#f39c12']
        )
        client_performance_fig.update_layout(**light_template['layout'])
        
        # Tabela de dados
        table = html.Div([
            dash_table.DataTable(
                data=df.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'backgroundColor': '#ffffff',
                    'color': '#2c3e50'
                },
                style_header={
                    'backgroundColor': '#f5f7fa',
                    'fontWeight': 'bold',
                    'color': '#3498db'
                }
            )
        ])
        
        # Formatar KPIs
        formatted_total = f"{int(total_pecas):,}".replace(',', '.')
        formatted_avg = f"{int(media_diaria):,}".replace(',', '.')
        formatted_in = f"{int(pecas_entrada):,}".replace(',', '.')
        formatted_out = f"{int(pecas_saida):,}".replace(',', '.')
        
        return [bar_fig, line_fig, pie_fig, comparison_fig, heatmap_fig, 
                formatted_total, formatted_avg, formatted_in, formatted_out,
                table, efficiency_comparison_fig, utilization_trend_fig, client_performance_fig]
                
    except Exception as e:
        print(f"Erro ao atualizar gráficos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return empty_charts()

# Função para criar gráficos vazios
def empty_charts():
    """Retorna gráficos vazios quando não há dados"""
    empty_fig = go.Figure().add_annotation(
        text="Nenhum dado encontrado para os filtros selecionados",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False
    )
    # Configurar tema claro para gráficos vazios
    empty_fig.update_layout(
        paper_bgcolor='#f5f7fa',
        plot_bgcolor='#f5f7fa',
        font=dict(color='#2c3e50')
    )
    return [empty_fig] * 5 + ["0"] * 4 + [html.Div("Nenhum dado encontrado")] + [empty_fig] * 3

# Adicionar media queries para melhorar a responsividade
@app.server.route('/assets/custom.css')
def serve_custom_css():
    custom_css = """
    .header-container {
        width: 100%;
    }
    
    @media (max-width: 1200px) {
        .header-container img {
            height: 150px !important;
        }
    }
    
    @media (max-width: 992px) {
        .chart-card {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        .kpi-card {
            flex: 1 1 calc(50% - 15px) !important;
        }
        
        .header-container img {
            height: 130px !important;
        }
        
        .header-container h1 {
            font-size: 1.8rem !important;
        }
    }
    
    @media (max-width: 768px) {
        .header-container {
            display: flex;
            justify-content: center;
        }
        
        .header-container > div {
            width: 100%;
            max-width: 700px;
        }
        
        .header-container img {
            height: 120px !important;
        }
        
        .header-container h1 {
            font-size: 1.6rem !important;
        }
        
        .filter-item {
            flex: 1 1 calc(50% - 10px) !important;
        }
    }
    
    @media (max-width: 576px) {
        .header-container > div {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: flex-start !important;
            flex-wrap: wrap !important;
        }
        
        .header-container img {
            height: 100px !important;
            margin-right: 15px !important;
        }
        
        .header-container h1 {
            font-size: 1.4rem !important;
            margin-bottom: 5px !important;
        }
        
        .header-container p {
            font-size: 1rem !important;
        }
        
        .kpi-card {
            flex: 1 1 100% !important;
        }
        
        .filter-item {
            flex: 1 1 100% !important;
        }
    }
    """
    return custom_css, 200, {'Content-Type': 'text/css'}

# Inicializar o aplicativo
if __name__ == '__main__':
    # Verificar e baixar o banco de dados se necessário
    download_database()
    
    # Encontrar uma porta disponível
    port = 8090
    max_port = 8099
    port_found = False
    
    while port <= max_port and not port_found:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            port_found = True
        except:
            port += 1
    
    if not port_found:
        import random
        port = random.randint(8000, 9000)
        print(f"Nenhuma porta no intervalo {8090}-{max_port} disponível. Usando porta aleatória: {port}")
    else:
        print(f"Porta disponível encontrada: {port}")
    
    print(f"Iniciando servidor Dash na porta {port}...")
    app.run(debug=True, host='0.0.0.0', port=port)
