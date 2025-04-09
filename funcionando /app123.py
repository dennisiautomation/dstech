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

# Configuração do aplicativo
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
server = app.server

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

# Layout do aplicativo
app.layout = html.Div([
    # Cabeçalho
    html.H1("Dashboard de Monitoramento de Lavanderia", className="text-center my-4"),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("Período:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=datetime.now() - timedelta(days=30),  # Últimos 30 dias como padrão
                end_date=datetime.now(),
                display_format='DD/MM/YYYY'
            )
        ], className="filter-item"),
        
        html.Div([
            html.Label("Máquina:"),
            dcc.Dropdown(
                id='machine-filter',
                options=[{'label': 'Todas', 'value': 'all'}] + 
                         [{'label': f'Máquina {i}', 'value': i} for i in range(1, 11)],
                value='all'
            )
        ], className="filter-item"),
        
        html.Div([
            html.Label("Cliente:"),
            dcc.Dropdown(
                id='client-filter',
                options=[{'label': 'Todos', 'value': 'all'}] + 
                         [{'label': f'Cliente {i}', 'value': i} for i in range(1, 6)],
                value='all'
            )
        ], className="filter-item"),
    ], className="filters-container"),
    
    # KPIs
    html.Div([
        html.Div([
            html.H3(id='kpi-total-pieces', children="0"),
            html.P("Total de Peças")
        ], className="kpi-card"),
        
        html.Div([
            html.H3(id='kpi-daily-avg', children="0"),
            html.P("Média Diária")
        ], className="kpi-card"),
        
        html.Div([
            html.H3(id='kpi-pieces-in', children="0"),
            html.P("Peças Entrada")
        ], className="kpi-card"),
        
        html.Div([
            html.H3(id='kpi-pieces-out', children="0"),
            html.P("Peças Saída")
        ], className="kpi-card"),
    ], className="kpi-container"),
    
    # Gráficos principais
    html.Div([
        html.Div([
            dcc.Graph(id='bar-chart')
        ], className="chart-card"),
        
        html.Div([
            dcc.Graph(id='line-chart')
        ], className="chart-card"),
        
        html.Div([
            dcc.Graph(id='pie-chart')
        ], className="chart-card"),
        
        html.Div([
            dcc.Graph(id='comparison-chart')
        ], className="chart-card"),
    ], className="charts-container"),
    
    # Gráficos adicionais
    html.Div([
        html.Div([
            dcc.Graph(id='heatmap-chart')
        ], className="chart-card-wide"),
        
        html.Div([
            dcc.Graph(id='efficiency-comparison-chart')
        ], className="chart-card-wide"),
        
        html.Div([
            dcc.Graph(id='utilization-trend-chart')
        ], className="chart-card-wide"),
        
        html.Div([
            dcc.Graph(id='client-performance-chart')
        ], className="chart-card-wide"),
    ], className="charts-container"),
    
    # Tabela de dados
    html.Div([
        html.Div(id='data-table', className="data-table-container")
    ], className="table-container"),
    
    # Elemento oculto para inicialização
    html.Div(id='initialization-trigger', children='init', style={'display': 'none'}),
    
    # Elemento oculto para filtros
    html.Div([
        dcc.RangeSlider(
            id='efficiency-filter',
            min=0,
            max=100,
            step=5,
            value=[0, 100]
        ),
        dcc.RangeSlider(
            id='utilization-filter',
            min=0,
            max=100,
            step=5,
            value=[0, 100]
        ),
    ], style={'display': 'none'}),
])

# Função para criar gráficos vazios
def empty_charts():
    """Retorna gráficos vazios quando não há dados"""
    empty_fig = go.Figure().add_annotation(
        text="Nenhum dado encontrado para os filtros selecionados",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False
    )
    return [empty_fig] * 5 + ["0"] * 4 + [html.Div("Nenhum dado encontrado")] + [empty_fig] * 3

# Callback para atualizar os gráficos
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
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('machine-filter', 'value'),
     Input('client-filter', 'value'),
     Input('efficiency-filter', 'value'),
     Input('utilization-filter', 'value'),
     Input('initialization-trigger', 'children')]
)
def update_charts(start_date, end_date, machine_filter, client_filter, efficiency_filter, utilization_filter, _):
    """Atualiza os gráficos e KPIs com base nos filtros selecionados"""
    print("\n" + "="*80)
    print("ATUALIZANDO GRÁFICOS")
    print("="*80)
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        print(f"Conectado ao banco de dados: {DB_PATH}")
        
        # Consulta SQL simples para obter todos os dados
        query = "SELECT * FROM DADOS"
        print(f"Query SQL: {query}")
        
        # Executar consulta
        df = pd.read_sql_query(query, conn)
        print(f"Registros retornados: {len(df)}")
        
        # Fechar conexão
        conn.close()
        
        # Se não houver dados, retornar gráficos vazios
        if df.empty:
            print("Nenhum dado encontrado")
            return empty_charts()
        
        # Converter a coluna de data para datetime
        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
        
        # Aplicar filtros
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['DATA'] >= start_date) & (df['DATA'] <= end_date)]
        
        if machine_filter and machine_filter != 'all':
            df = df[df['MAQUINA'] == int(machine_filter)]
        
        if client_filter and client_filter != 'all':
            df = df[df['LINHA'] == int(client_filter)]
        
        # Se não houver dados após filtros, retornar gráficos vazios
        if df.empty:
            print("Nenhum dado encontrado após aplicar filtros")
            return empty_charts()
        
        # Calcular eficiência e utilização
        df['EFICIENCIA'] = ((df['EF_ENTRADA'] + df['EF_SAIDA']) / 2).fillna(0).clip(0, 100)
        
        # Evitar divisão por zero
        total_tempo = df['TEMPO_MAQ_LIGADA'] + df['TEMPO_MAQ_PARADA']
        df['UTILIZACAO'] = np.where(total_tempo > 0, 
                                    (df['TEMPO_MAQ_LIGADA'] / total_tempo) * 100, 
                                    0).clip(0, 100)
        
        # Calcular KPIs
        total_pecas_in = df['PECAS_TOT_ENT'].sum()
        total_pecas_out = df['PECAS_TOT_SAI'].sum()
        total_pecas = total_pecas_in + total_pecas_out
        
        # Calcular média diária
        dias_unicos = df['DATA'].dt.date.nunique()
        media_diaria = total_pecas / max(dias_unicos, 1)  # Evitar divisão por zero
        
        # 1. Gráfico de barras - Produção por máquina
        bar_fig = px.bar(
            df.groupby('MAQUINA')['PECAS_TOT_ENT'].sum().reset_index(),
            x='MAQUINA',
            y='PECAS_TOT_ENT',
            title='Produção por Máquina'
        )
        
        # 2. Gráfico de linha - Tendência de produção
        line_data = df.groupby(df['DATA'].dt.date)['PECAS_TOT_ENT'].sum().reset_index()
        line_fig = px.line(
            line_data,
            x='DATA',
            y='PECAS_TOT_ENT',
            title='Tendência de Produção'
        )
        
        # 3. Gráfico de pizza - Distribuição por cliente
        pie_fig = px.pie(
            df.groupby('LINHA')['PECAS_TOT_ENT'].sum().reset_index(),
            values='PECAS_TOT_ENT',
            names='LINHA',
            title='Distribuição por Cliente'
        )
        
        # 4. Gráfico de comparação - Entrada vs Saída
        comparison_data = pd.DataFrame({
            'Tipo': ['Entrada', 'Saída'],
            'Quantidade': [total_pecas_in, total_pecas_out]
        })
        comparison_fig = px.bar(
            comparison_data,
            x='Tipo',
            y='Quantidade',
            title='Comparação Entrada vs Saída',
            color='Tipo'
        )
        
        # 5. Mapa de calor - Produção por dia e hora
        df['DiaSemana'] = df['DATA'].dt.day_name()
        df['Hora'] = df['DATA'].dt.hour
        heatmap_data = df.groupby(['DiaSemana', 'Hora'])['PECAS_TOT_ENT'].sum().reset_index()
        heatmap_fig = px.density_heatmap(
            heatmap_data,
            x='Hora',
            y='DiaSemana',
            z='PECAS_TOT_ENT',
            title='Produção por Dia e Hora'
        )
        
        # 6. Gráfico de eficiência por máquina
        efficiency_fig = px.bar(
            df.groupby('MAQUINA')['EFICIENCIA'].mean().reset_index(),
            x='MAQUINA',
            y='EFICIENCIA',
            title='Eficiência por Máquina'
        )
        
        # 7. Gráfico de tendência de utilização
        utilization_data = df.groupby(df['DATA'].dt.date)['UTILIZACAO'].mean().reset_index()
        utilization_fig = px.line(
            utilization_data,
            x='DATA',
            y='UTILIZACAO',
            title='Tendência de Utilização'
        )
        
        # 8. Gráfico de desempenho por cliente
        client_fig = px.bar(
            df.groupby('LINHA')['PECAS_TOT_ENT'].sum().reset_index(),
            x='LINHA',
            y='PECAS_TOT_ENT',
            title='Desempenho por Cliente'
        )
        
        # Tabela de dados
        table = html.Div([
            html.H4("Dados Detalhados"),
            dash_table.DataTable(
                data=df.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
            )
        ])
        
        # Formatar KPIs
        kpi_total = f"{int(total_pecas):,}"
        kpi_daily = f"{int(media_diaria):,}"
        kpi_in = f"{int(total_pecas_in):,}"
        kpi_out = f"{int(total_pecas_out):,}"
        
        print(f"KPIs calculados: Total={kpi_total}, Média={kpi_daily}, Entrada={kpi_in}, Saída={kpi_out}")
        print("Gráficos atualizados com sucesso")
        
        return [bar_fig, line_fig, pie_fig, comparison_fig, heatmap_fig,
                kpi_total, kpi_daily, kpi_in, kpi_out, table,
                efficiency_fig, utilization_fig, client_fig]
                
    except Exception as e:
        print(f"ERRO ao atualizar gráficos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return empty_charts()

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
