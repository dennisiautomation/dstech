from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from flask_login import current_user
from users import get_users

def create_settings_layout():
    """Cria o layout da página de configurações"""
    # Verifica se o usuário está autenticado e é admin
    if not current_user.is_authenticated or not current_user.is_admin:
        return html.Div([
            html.H3("Acesso Negado", className="text-danger"),
            html.P("Você não tem permissão para acessar esta página."),
            dbc.Button("Voltar ao Dashboard", href="/", color="primary")
        ], className="p-5")
    
    # Obtém a lista de usuários
    users_data = get_users()
    users_list = []
    
    for user_id, user_data in users_data.items():
        users_list.append({
            "ID": user_id,
            "Usuário": user_data["username"],
            "Email": user_data.get("email", ""),
            "Admin": "Sim" if user_data.get("is_admin", False) else "Não"
        })
    
    return html.Div([
        html.H2("Configurações do Sistema", className="mb-4"),
        
        # Seção de gerenciamento de usuários
        html.Div([
            html.H4("Gerenciamento de Usuários", className="mb-3"),
            
            # Formulário para adicionar usuário
            dbc.Card([
                dbc.CardHeader("Adicionar Novo Usuário"),
                dbc.CardBody([
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
                    ])
                ])
            ], className="mb-4"),
            
            # Alerta para feedback
            dbc.Alert(
                id="user-alert",
                dismissable=True,
                is_open=False,
                duration=4000
            ),
            
            # Tabela de usuários
            html.H5("Usuários Cadastrados", className="mb-3"),
            dash_table.DataTable(
                id='users-table',
                columns=[
                    {"name": "ID", "id": "ID"},
                    {"name": "Usuário", "id": "Usuário"},
                    {"name": "Email", "id": "Email"},
                    {"name": "Admin", "id": "Admin"},
                    {"name": "", "id": "actions", "presentation": "markdown"}
                ],
                data=users_list,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #dee2e6'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    }
                ],
                row_selectable=False,
                page_size=10
            )
        ]),
        
        # Botão para voltar ao dashboard
        html.Div([
            dbc.Button("Voltar ao Dashboard", href="/", color="primary", className="mt-4")
        ], className="d-flex justify-content-end"),
        
        # Stores para gerenciar estados
        dcc.Store(id="edit-user-id", storage_type="memory"),
        
        # Modal para editar usuário
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Editar Usuário")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Nome de Usuário"),
                        dbc.Input(id="edit-username", type="text")
                    ], width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Email"),
                        dbc.Input(id="edit-email", type="email")
                    ], width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Nova Senha (deixe em branco para manter a atual)"),
                        dbc.Input(id="edit-password", type="password", placeholder="Nova senha")
                    ], width=12, className="mb-3"),
                    dbc.Col([
                        dbc.Checkbox(
                            id="edit-is-admin",
                            label="Usuário Administrador"
                        )
                    ], width=12)
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="cancel-edit", className="me-2"),
                dbc.Button("Salvar Alterações", id="save-edit", color="success")
            ])
        ], id="edit-user-modal"),
        
        # Modal de confirmação para excluir usuário
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirmar Exclusão")),
            dbc.ModalBody("Tem certeza que deseja excluir este usuário? Esta ação não pode ser desfeita."),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="cancel-delete", className="me-2"),
                dbc.Button("Excluir", id="confirm-delete", color="danger")
            ])
        ], id="delete-confirm-modal")
    ], className="p-4")
