from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user, current_user
from users import get_user_by_email

def create_login_layout():
    """Cria o layout da página de login"""
    return html.Div([
        html.Div([
            html.Img(src='/assets/logo.png', style={'height': '180px', 'margin-bottom': '30px'}),
            html.H2("Login do Sistema", className="mb-4", style={'color': '#2c3e50', 'font-weight': '700'}),
            dbc.Alert(
                "Email ou senha incorretos. Tente novamente.",
                id="login-alert",
                color="danger",
                dismissable=True,
                is_open=False,
            ),
            html.Form([
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
            ]),
        ], style={
            'width': '400px',
            'margin': '100px auto',
            'padding': '30px',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
            'borderRadius': '8px',
            'backgroundColor': 'white',
            'textAlign': 'center'
        }),
        # Store para armazenar o estado de autenticação
        dcc.Store(id='auth-store', storage_type='session'),
    ])

def validate_login(email, password):
    """Valida as credenciais de login"""
    user = get_user_by_email(email)
    if user and user.check_password(password):
        login_user(user)
        return True, user
    return False, None

def create_logout():
    """Realiza o logout do usuário"""
    logout_user()
    return True
