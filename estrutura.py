# -*- coding: utf-8 -*-
"""estrutura.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SiAX_nByBZsXkuO4Ax5-vIOOPZL_vJDr

# Puxando os dados do Analytics
"""
# !pip install dash dash-bootstrap-components plotly flask
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, DateRange, Dimension, Metric
import requests
from datetime import datetime, timedelta
from flask import Flask
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import warnings

# Suprimir todos os warnings
warnings.filterwarnings("ignore")

"""# Puxando os dados da API do Pipedrive

"""

# Defina o seu API Token do Pipedrive
API_TOKEN = 'bbdd39fba4dab68ac0c03f4a629680f7429478ff'
BASE_URL = 'https://api.pipedrive.com/v1/'

# Função para extrair todos os dados de negócios utilizando paginação
def fetch_all_pipedrive_deals():
    all_deals = []
    start = 0
    limit = 100  # Número de registros por página

    while True:
        url = f'{BASE_URL}deals?start={start}&limit={limit}&api_token={API_TOKEN}'
        response = requests.get(url)

        if response.status_code == 200:
            deals = response.json().get('data', [])
            if not deals:
                break  # Encerra o loop se não houver mais dados

            all_deals.extend(deals)  # Adiciona os registros atuais à lista geral
            start += limit  # Atualiza o offset para a próxima página
        else:
            print(f"Erro ao extrair dados do Pipedrive: {response.status_code}")
            break

    # Converte todos os negócios extraídos em um DataFrame
    df_all_deals = pd.DataFrame(all_deals)
    print(f"Negócios do Pipedrive extraídos com sucesso. Total de registros: {len(df_all_deals)}")
    return df_all_deals

# Extraindo todos os dados de negócios
df_pipedrive = fetch_all_pipedrive_deals()

"""# Puxando as etiquetas"""

# Carregar o arquivo etiquetas.xlsx
df_etiquetas = pd.read_excel('etiquetas.xlsx')

# Substituir valores nulos por 0
df_etiquetas = df_etiquetas.fillna(0)

# Salvar como CSV
df_etiquetas.to_csv('etiquetas.csv', index=False)
# print("Arquivo etiquetas.xlsx convertido para etiquetas.csv com sucesso e valores nulos substituídos por 0.")

# Carregar o arquivo etiquetas.xlsx
df_etiquetas = pd.read_excel('etiquetas.xlsx')

# Separar a coluna "Data Inscrição" para evitar alterações
coluna_data = df_etiquetas['Data Inscrição']

# Aplicar as mudanças nas outras colunas, exceto "Data Inscrição"
df_etiquetas = df_etiquetas.drop(columns=['Data Inscrição'])  # Remover temporariamente "Data Inscrição"
df_etiquetas = df_etiquetas.apply(pd.to_numeric, errors='coerce').fillna(0)  # Substituir nulos e valores não numéricos por 0
df_etiquetas = df_etiquetas.astype(int)  # Converter colunas numéricas de float para int

# Renomear a coluna 'Telefone' para 'numero_wpp'
df_etiquetas = df_etiquetas.rename(columns={'Telefone': 'numero_wpp'})

# Adicionar um '+' antes de todos os valores na coluna 'numero_wpp'
df_etiquetas['numero_wpp'] = df_etiquetas['numero_wpp'].apply(lambda x: f'+{x}')

# Recolocar a coluna "Data Inscrição" de volta ao DataFrame
df_etiquetas['Data Inscrição'] = coluna_data

# df_etiquetas

df_hermes= pd.read_excel('hermes.xlsx')
df_gabi = pd.read_excel('gabi.xlsx')
df_contratog = pd.read_excel('contratog.xlsx')
df_contratoh = pd.read_excel('contratoh.xlsx')

# """# Puxando os dados do endpoint"""

# # Função para buscar todos os dados do endpoint
# def fetch_all_data(url):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             return pd.DataFrame(data)  # Converte os dados em um DataFrame
#         else:
#             print(f"Error: {response.status_code}, Detail: {response.json().get('detail', 'No detail provided')}")
#     except requests.RequestException as e:
#         print(f"Failed to make the request: {e}")
#         return pd.DataFrame()

# # URL do endpoint
# url = "https://web-production-c353.up.railway.app/retrieve_all"

# # Chamando a função e obtendo os dados
# df_endpoint = fetch_all_data(url)

# # Verificação básica dos dados
# if df_endpoint.empty:
#     print("Os dados não foram carregados corretamente. Verifique o endpoint ou o formato dos dados.")
#     exit()

# # Função para calcular o tempo em cada etapa com base nas colunas de timestamp
# def calculate_stage_duration(row):
#     created_at = pd.to_datetime(row['created_at'], errors='coerce')
#     last_modified = pd.to_datetime(row['last_modified'], errors='coerce')
#     if pd.isnull(created_at) or pd.isnull(last_modified):
#         return 0  # Retorna 0 se houver erro de conversão
#     duration = (last_modified - created_at).total_seconds() / 60  # Duração em minutos
#     return duration

# # Função para extrair a última etapa (flag) alcançada na jornada
# def extract_final_stage(raw_data):
#     try:
#         flags = {
#             'voo': int(raw_data.get('FLAG_VOO_JORNADA', 0)),
#             'negativacao': int(raw_data.get('FLAG_NEGATIVACAO_JORNADA', 0)),
#             'telefonia': int(raw_data.get('FLAG_SERV_TELEF_JORNADA', 0)),
#             'bancario': int(raw_data.get('FLAG_SERV_BANCARIO_JORNADA', 0)),
#             'compra_online': int(raw_data.get('FLAG_COMPRA_ONLINE_JORNADA', 0)),
#             'outros': int(raw_data.get('FLAG_OUTROS_JORNADA', 0)),
#             'hospedagem': int(raw_data.get('FLAG_HOSPEDAGEM_JORNADA', 0))
#         }
#         final_stage = max(flags.values())  # Encontra a maior flag para determinar a etapa final
#         return final_stage
#     except Exception as e:
#         print(f"Erro ao extrair etapa final: {e}")
#         return 0

# # Aplicar as funções ao dataframe
# df_endpoint['created_at'] = pd.to_datetime(df_endpoint['created_at'], errors='coerce')
# df_endpoint['Tempo_na_Etapa'] = df_endpoint.apply(calculate_stage_duration, axis=1)
# df_endpoint['Etapa_Final'] = df_endpoint['RAW_DATA'].apply(extract_final_stage)
# # Substituir valores NaN por 0 em todas as colunas do df_endpoint
# df_endpoint = df_endpoint.fillna(0)

# # Lista de colunas de interesse
# columns = [
#     'FLAG_HOSPEDAGEM_JORNADA',
#     'FLAG_OUTROS_JORNADA',
#     'FLAG_VOO_JORNADA',
#     'FLAG_COMPRA_ONLINE_JORNADA',
#     'FLAG_SERV_BANCARIO_JORNADA',
#     'FLAG_NEGATIVACAO_JORNADA',
#     'FLAG_SERV_TELEF_JORNADA'
# ]

# # Converter as colunas para numérico, ignorando erros e preenchendo com NaN para valores não convertíveis
# for col in columns:
#     df_endpoint[col] = pd.to_numeric(df_endpoint[col], errors='coerce')

# # Calcular o valor máximo para cada coluna
# max_values = {col: df_endpoint[col].max() for col in columns}

# # Determinar o valor máximo global entre todas as flags
# max_global = max(max_values.values())

# print("Valores máximos de cada coluna:")
# for col, max_val in max_values.items():
#     print(f"{col}: {max_val}")

# print(f"Valor máximo global: {max_global}")

# # Criar a coluna FLAG_FINAL, onde 1 indica que a pessoa chegou ao fim e 0 indica que não
# df_endpoint['FLAG_FINAL'] = df_endpoint[columns].max(axis=1).apply(lambda x: 1 if x == max_global else 0)

# # # Exibir as primeiras linhas para ver o resultado
# # print(df_endpoint[['FLAG_FINAL'] + columns].head())

"""# Unificação e tratamento de dados"""

# Duplicar os DataFrames
# df_endpoint_dup = df_endpoint
df_pipedrive_dup = df_pipedrive
df_etiquetas_dup = df_etiquetas
df_tudao2 = df_etiquetas.copy()

# Adicionando a nova coluna 'Atribuidos' com o valor 1 para todas as linhas
df_gabi['Atribuidos'] = 1

# Adicionando a nova coluna 'Atribuidos' com o valor 1 para todas as linhas
df_hermes['Atribuidos'] = 2

df_atribuido = pd.concat([df_gabi, df_hermes], ignore_index=True)

df_contratog['Contrato'] = 1

df_contratoh['Contrato'] = 2

df_contrato= pd.concat([df_contratog, df_contratoh], ignore_index=True)

# Supondo que df_contrato e df_atribuido já estejam definidos

# Fazendo o merge/junção pela coluna "Telefone", mantendo todos os valores do df_atribuido
df_atendentes = pd.merge(df_atribuido, df_contrato, on='Telefone', how='left')

# Preenchendo os valores NaN de DDD_x com os valores de DDD_y e removendo as colunas duplicadas
df_atendentes['DDD'] = df_atendentes['DDD_x'].combine_first(df_atendentes['DDD_y'])
df_atendentes['Data Inscrição'] = df_atendentes['Data Inscrição_x'].combine_first(df_atendentes['Data Inscrição_y'])

# Agora, podemos remover as colunas duplicadas (_x e _y)
df_atendentes = df_atendentes.drop(columns=['DDD_x', 'DDD_y', 'Data Inscrição_x', 'Data Inscrição_y'])

# Convertendo as colunas 'DDD' e 'Contrato' para o tipo int, primeiro tratando possíveis NaN que possam existir
df_atendentes['DDD'] = df_atendentes['DDD'].fillna(0).astype(int)
df_atendentes['Contrato'] = df_atendentes['Contrato'].fillna(0).astype(int)

# Renomeando a coluna 'Telefone' no df_atendentes para 'numero_wpp'
df_atendentes.rename(columns={'Telefone': 'numero_wpp'}, inplace=True)

# Adicionar um '+' antes de todos os valores na coluna 'numero_wpp'
df_atendentes['numero_wpp'] = df_atendentes['numero_wpp'].apply(lambda x: f'+{x}')

# Realizando o merge, mantendo todos os valores de 'numero_wpp' no df_tudao2
df_merged = pd.merge(df_tudao2, df_atendentes, on='numero_wpp', how='left')

# Preenchendo os valores NaN de DDD_x com os valores de DDD_y e removendo as colunas duplicadas
df_merged['DDD'] = df_merged['DDD_x'].combine_first(df_merged['DDD_y'])
df_merged['Data Inscrição'] = df_merged['Data Inscrição_x'].combine_first(df_merged['Data Inscrição_y'])

# Agora, podemos remover as colunas duplicadas (_x e _y)
df_merged = df_merged.drop(columns=['DDD_x', 'DDD_y', 'Data Inscrição_x', 'Data Inscrição_y'])

# Convertendo as colunas 'DDD' e 'Contrato' para o tipo int, primeiro tratando possíveis NaN que possam existir
df_merged['DDD'] = df_merged['DDD'].fillna(0)
df_merged['Contrato'] = df_merged['Contrato'].fillna(0)
df_merged['Atribuidos'] = df_merged['Atribuidos'].fillna(0)

# Dicionário para mapear os DDDs aos estados
ddd_mapping_estados = {
    61: 'Distrito Federal',
    62: 'Goiás', 64: 'Goiás',
    65: 'Mato Grosso', 66: 'Mato Grosso',
    67: 'Mato Grosso do Sul',
    82: 'Alagoas',
    71: 'Bahia', 73: 'Bahia', 74: 'Bahia', 75: 'Bahia', 77: 'Bahia',
    85: 'Ceará', 88: 'Ceará',
    98: 'Maranhão', 99: 'Maranhão',
    83: 'Paraíba',
    81: 'Pernambuco', 87: 'Pernambuco',
    86: 'Piauí', 89: 'Piauí',
    84: 'Rio Grande do Norte',
    79: 'Sergipe',
    68: 'Acre',
    96: 'Amapá',
    92: 'Amazonas', 97: 'Amazonas',
    91: 'Pará', 93: 'Pará', 94: 'Pará',
    69: 'Rondônia',
    95: 'Roraima',
    63: 'Tocantins',
    27: 'Espírito Santo', 28: 'Espírito Santo',
    31: 'Minas Gerais', 32: 'Minas Gerais', 33: 'Minas Gerais', 34: 'Minas Gerais',
    35: 'Minas Gerais', 37: 'Minas Gerais', 38: 'Minas Gerais',
    21: 'Rio de Janeiro', 22: 'Rio de Janeiro', 24: 'Rio de Janeiro',
    11: 'São Paulo', 12: 'São Paulo', 13: 'São Paulo', 14: 'São Paulo',
    15: 'São Paulo', 16: 'São Paulo', 17: 'São Paulo', 18: 'São Paulo', 19: 'São Paulo',
    41: 'Paraná', 42: 'Paraná', 43: 'Paraná', 44: 'Paraná', 45: 'Paraná', 46: 'Paraná',
    51: 'Rio Grande do Sul', 53: 'Rio Grande do Sul', 54: 'Rio Grande do Sul', 55: 'Rio Grande do Sul',
    47: 'Santa Catarina', 48: 'Santa Catarina', 49: 'Santa Catarina'
}

# Função para garantir que o DDD é numérico e tratar erros
def tratar_ddd(ddd):
    try:
        return int(ddd)
    except ValueError:
        return None

# Tratando os valores de DDD
df_merged['DDD'] = df_merged['DDD'].apply(tratar_ddd)

# Aplicar o mapeamento de DDDs para Estados usando .loc para evitar SettingWithCopyWarning
df_merged.loc[:, 'Estado'] = df_merged['DDD'].map(ddd_mapping_estados)

import pandas as pd

# Convertendo a coluna 'Data Inscrição' para o formato datetime
df_merged['Data Inscrição'] = pd.to_datetime(df_merged['Data Inscrição'], errors='coerce')

# Quebrar a coluna 'title' no df_pipedrive_dup em três colunas
df_pipedrive_dup[['id2', 'Problema2', 'numero_wpp']] = df_pipedrive_dup['title'].str.extract(r'(\d+)\s*-\s*(.*?)\s*-\s*(\+\d+)')

# Remover a coluna original 'title' depois de extrair os valores
df_pipedrive_dup.drop('title', axis=1, inplace=True)

# Selecionando as colunas 'numero_wpp' e 'lost reason' do df_pipedrive_dup
df_separado = df_pipedrive_dup[['numero_wpp', 'lost_reason']]

# Dropping duplicate 'numero_wpp' values in df_separado, keeping the first occurrence
df_separado_unique = df_separado.drop_duplicates(subset='numero_wpp', keep='first')
# Perform the merge again after handling duplicates
df_merged = pd.merge(df_merged, df_separado_unique, on='numero_wpp', how='left')

# Calculando a soma de cada valor único na coluna 'lost reason'
lost_reason_counts = df_merged['lost_reason'].value_counts()

# Substituir todos os valores nulos por 0, exceto na coluna 'lost_reason'
df_merged = df_merged.apply(lambda col: col.fillna(0) if col.name != 'lost_reason' else col)

import requests
import pytz  # Import pytz for time zone handling
import pandas as pd
from flask import Flask, request, Response
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import warnings
from flask_httpauth import HTTPBasicAuth


# Suprimir todos os warnings
warnings.filterwarnings("ignore")

# Authentication setup
auth = HTTPBasicAuth()

# Define a dictionary of users and passwords
users = {
    "Admin": "Solucionai467"  # You can replace these with your actual username and password
}

# Function to authenticate users
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


# Dash and Flask app initialization
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                               "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
                                                               "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap"],
                suppress_callback_exceptions=True)

# Middleware to apply authentication to Dash routes
@server.before_request
@auth.login_required
def authenticate():
    pass  # Authentication is handled by HTTPBasicAuth


# Pega o token da variável de ambiente
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_last_commit_date(owner, repo, file_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file_path}&per_page=1"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        commit_info = response.json()[0]
        commit_date_utc = pd.to_datetime(commit_info['commit']['committer']['date'])

        # Convert to São Paulo timezone
        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        commit_date_saopaulo = commit_date_utc.tz_convert(saopaulo_tz)
        commit_date_formatted = commit_date_saopaulo.strftime('%d/%m às %H:%M')
        return commit_date_formatted
    else:
        return "02/12/2024 às 22:39"

# Fetching the last update time from GitHub for each XLSX file
owner = "solucionai"
repo = "dashboard"
files = ["etiquetas.xlsx", "gabi.xlsx", "hermes.xlsx", "contratoh.xlsx", "contratog.xlsx"]

last_update_times = [get_last_commit_date(owner, repo, file) for file in files]

# Assuming all files are updated at the same time, you can use the first one
last_update_display = last_update_times[0]

# Assuming df_merged is defined and pre-processed with 'Data Inscrição' column in datetime format
df_merged['Data Inscrição'] = pd.to_datetime(df_merged['Data Inscrição'], errors='coerce')

# Calculate total people and total days
total_pessoas = df_merged.shape[0]
total_dias = (df_merged['Data Inscrição'].max() - df_merged['Data Inscrição'].min()).days
media_pessoas_dia = total_pessoas / total_dias if total_dias > 0 else 0

# Calculate total signed contracts
total_contratos_assinados = df_merged[df_merged['CONTRATO ASSINADO'] == 1].shape[0]

# Card styles (Updated with FontAwesome icons and new font)
CARD_STYLE_UPDATED = {
    "padding": "20px",
    "border-radius": "10px",
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "text-align": "center",
    "margin": "20px",
    "background-color": "#f8f9fa",
    "color": "#343a40",
    "font-family": "'Roboto', sans-serif",
}

CARD_STYLE_BLUE = {
    "padding": "20px",
    "border-radius": "10px",
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "text-align": "center",
    "margin": "20px",
    "background-color": "#17a2b8",
    "color": "white",
    "font-family": "'Roboto', sans-serif",
}

CARD_STYLE_GREEN = {
    "padding": "20px",
    "border-radius": "10px",
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "text-align": "center",
    "margin": "20px",
    "background-color": "#28a745",
    "color": "white",
    "font-family": "'Roboto', sans-serif",
}

# Define metric cards with FontAwesome icons
card_total_pessoas = html.Div([
    html.H4([html.I(className="fas fa-users", style={"margin-right": "10px"}), "Total de Pessoas na Base"],
            style={"margin-bottom": "10px"}),
    html.Div(f"{total_pessoas}", style={"font-size": "36px", "font-weight": "bold"}),
], style=CARD_STYLE_UPDATED)

card_media_pessoas_dia = html.Div([
    html.H4([html.I(className="fas fa-calendar-day", style={"margin-right": "10px"}), "Média de Pessoas por Dia"],
            style={"margin-bottom": "10px"}),
    html.Div(f"{media_pessoas_dia:.2f}", style={"font-size": "36px", "font-weight": "bold"}),
], style=CARD_STYLE_BLUE)

card_contratos_assinados = html.Div([
    html.H4([html.I(className="fas fa-file-signature", style={"margin-right": "10px"}), "Total de Contratos Assinados"],
            style={"margin-bottom": "10px"}),
    html.Div(f"{total_contratos_assinados}", style={"font-size": "36px", "font-weight": "bold"}),
], style=CARD_STYLE_GREEN)

# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "20px",
    "background-color": "#343a40",
}

CONTENT_STYLE = {
    "margin-left": "20%",
    "padding": "20px",
    "background-color": "#f8f9fa",
    "text-align": "center",
    "font-family": "'Roboto', sans-serif",
}

# Add "last update" information to be displayed on the dashboard
last_update_text = html.Div([
    html.H5(f"Última atualização feita em {last_update_display}",
            style={"color": "black", "font-family": "'Roboto', sans-serif"})
])

# Sidebar layout with the new problem filter
sidebar = html.Div(
    [
        html.H2("Dashboard", className="display-6", style={"color": "white", "font-family": "'Roboto', sans-serif"}),
        html.Hr(),
        html.P("Solucionaí", className="lead", style={"color": "white", "font-family": "'Roboto', sans-serif"}),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", id="home-button", style={"color": "white"}),
                dbc.NavLink("Leads", href="/leads", id="leads-button", style={"color": "white"}),
                dbc.NavLink("Atendentes", href="/atendentes", id="atendentes-button", style={"color": "white"}),
            ],
            vertical=True,
            pills=True,
        ),
        # New problem filter dropdown added here
        html.Div([
            html.H5("Filtrar por Problema", style={"margin-top": "20px", "color": "white", "font-family": "'Roboto', sans-serif"}),
            dcc.Dropdown(
                id='problem-filter',
                options=[
                    {'label': 'Nenhum', 'value': 'Nenhum'},  # Default option
                    {'label': 'Outros', 'value': 'Outros'},
                    {'label': 'Negativação', 'value': 'Negativação'},
                    {'label': 'Compras Online', 'value': 'Compras Online'},
                    {'label': 'Serviços Bancários', 'value': 'Serviços Bancários'},
                    {'label': 'Telefonia', 'value': 'Telefonia'}
                ],
                value='Nenhum',  # Default value
                clearable=False,
                style={"margin-bottom": "20px"}
            )
        ])
    ],
    style=SIDEBAR_STYLE,
)

# Date range picker for filtering the data
date_picker = html.Div([
    html.H5("Selecionar Período de Datas", style={"margin-bottom": "10px", "font-family": "'Roboto', sans-serif"}),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df_merged['Data Inscrição'].min().date(),
        end_date=df_merged['Data Inscrição'].max().date(),
        display_format='DD-MM-YYYY',
        style={"margin-bottom": "20px"}
    )
])

content = html.Div(
    [
        html.H2("Dashboard de Dados Solucionaí", className="display-4", style={"font-family": "'Roboto', sans-serif"}),
        html.Hr(),
        last_update_text,  # Add last update text here
        date_picker,
        html.Div(id="page-content"),
    ],
    style=CONTENT_STYLE,
)

app.layout = html.Div([sidebar, content])

# Callback to handle page navigation (buttons)
@app.callback(
    Output("page-content", "children"),
    [Input("home-button", "n_clicks"),
     Input("leads-button", "n_clicks"),
     Input("atendentes-button", "n_clicks")]
)
def display_page(n_home, n_leads, n_atendentes):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.H3("Home, seja bem-vindo ao Dashboard de Dados da Solucionaí!",
                       style={"font-family": "'Roboto', sans-serif"})
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "home-button":
            return html.H3("Home, seja bem-vindo ao Dashboard de Dados da Solucionaí!",
                           style={"font-family": "'Roboto', sans-serif"})
        elif button_id == "leads-button":
            return html.Div(id='leads-content')
        elif button_id == "atendentes-button":
            return html.Div(id='atendentes-content')

# Callback to handle the date range picker and the problem filter, updating Leads graphs
@app.callback(
    Output("leads-content", "children"),
    [Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date"),
     Input("problem-filter", "value")]
)
def update_leads_content(start_date, end_date, selected_problem):
    # Convert the date range values to datetime
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    else:
        start_date = df_merged['Data Inscrição'].min()
        end_date = df_merged['Data Inscrição'].max()

    # Filter the DataFrame based on the selected date range
    filtered_df = df_merged[(df_merged['Data Inscrição'] >= start_date) & (df_merged['Data Inscrição'] <= end_date)]

    # Apply the problem filter if it's not "Nenhum"
    if selected_problem != "Nenhum":
        filtered_df = filtered_df[filtered_df[selected_problem] > 0]

    # Handle the case where no data is available for the selected range
    if filtered_df.empty:
        return html.Div("Nenhum dado disponível para o intervalo selecionado.")

    # Gráfico 1: Total de Leads Cadastrados na Base por Período de Tempo
    leads_by_date = filtered_df.groupby(filtered_df['Data Inscrição'].dt.date).size()
    fig_total_leads = px.line(x=leads_by_date.index, y=leads_by_date.values, title="Total de Leads por Período",
                              labels={'x': 'Data', 'y': 'Número de Leads'})

    fig_total_leads.update_traces(line=dict(color="#17a2b8", width=1.5, dash="solid"),
                                  marker=dict(size=6, color="#fd7e14"))
    fig_total_leads.add_scatter(
        x=leads_by_date.index,
        y=leads_by_date.values,
        mode='markers+text',
        text=leads_by_date.values,
        textposition="top center",
        textfont=dict(size=10),
        showlegend=False
    )
    fig_total_leads.update_layout(
        xaxis=dict(range=[leads_by_date.index.min(), leads_by_date.index.max()]),
        plot_bgcolor="light grey",
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        transition=dict(duration=500)
    )

    # Gráfico 2: Contratos Fechados por Período
    contratos_by_date = filtered_df[filtered_df['CONTRATO ASSINADO'] == 1].groupby(filtered_df['Data Inscrição'].dt.date).size()
    fig_contratos_tempo = px.line(x=contratos_by_date.index, y=contratos_by_date.values, title="Contratos Fechados por Período",
                                  labels={'x': 'Data', 'y': 'Número de Contratos Fechados'})

    fig_contratos_tempo.update_traces(line=dict(color="#28a745", width=1.5), marker=dict(size=6, color="#fd7e14"))
    # Add numbers above the points
    fig_contratos_tempo.add_scatter(
        x=contratos_by_date.index,
        y=contratos_by_date.values,
        mode='markers+text',
        text=contratos_by_date.values,
        textposition='top center',
        textfont=dict(size=10),
        showlegend=False
    )
    # Set x-axis to start and end at the actual data range
    fig_contratos_tempo.update_layout(
        xaxis=dict(range=[contratos_by_date.index.min(), contratos_by_date.index.max()]),
        plot_bgcolor="light grey",
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        transition=dict(duration=500)
    )

    # Gráfico 3: Leads por Tipo de Problema (não é afetado pelo filtro de problema)
    leads_by_problem = df_merged[['Aviação', 'Outros', 'Hospedagem', 'Negativação', 'Compras Online', 'Serviços Bancários', 'Telefonia']].sum().sort_values(ascending=False)
    fig_leads_problema = px.bar(x=leads_by_problem.index, y=leads_by_problem.values,
                                title="Leads por Tipo de Problema",
                                labels={'x': 'Tipo de Problema', 'y': 'Contagem de Leads'})

    fig_leads_problema.update_traces(marker_color="#fd7e14", marker_line_color="#2c3e50", marker_line_width=1.5)
    fig_leads_problema.update_layout(
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        bargap=0.2
    )

    # Gráfico 4: Leads por Região ou DDD
    leads_by_ddd = filtered_df['Estado'].value_counts()
    leads_by_ddd = leads_by_ddd[leads_by_ddd > 9]
    fig_leads_ddd = px.bar(x=leads_by_ddd.index, y=leads_by_ddd.values, title="Leads por Região",
                           labels={'x': 'Estado', 'y': 'Contagem de Leads'})

    fig_leads_ddd.update_traces(marker_color="#17a2b8", marker_line_color="#2c3e50", marker_line_width=1.5)
    fig_leads_ddd.update_layout(
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        bargap=0.2
    )

    # Gráfico 5: Leads que Completaram o Fluxo até o Final
    completed_flow = filtered_df[filtered_df['COMPLETOU_O_FLUXO'] == 1].shape[0]
    fig_fluxo_completo = px.pie(values=[completed_flow, filtered_df.shape[0] - completed_flow],
                                names=['Completaram', 'Não Completaram'],
                                title="Leads que Completaram o Fluxo até o Final")

    fig_fluxo_completo.update_traces(
        marker=dict(colors=["#007bff", "#ffc107"], line=dict(color='#2c3e50', width=1.5)),
        textinfo="percent+label",
        hoverinfo="label+percent",
        pull=[0.1, 0]
    )
    fig_fluxo_completo.update_layout(
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Gráfico 6: Leads que Não Prosseguiram após o Primeiro Contato
    leads_nao_prosseguiram = filtered_df[(filtered_df['ClienteDesistiu'] == 1) | (filtered_df['SEM RESPOSTA'] == 1)].shape[0]
    fig_leads_nao_prosseguiram = px.pie(values=[leads_nao_prosseguiram, filtered_df.shape[0] - leads_nao_prosseguiram],
                                        names=['Não Prosseguiram', 'Prosseguiram'],
                                        title="Leads que Não Prosseguiram após o Primeiro Contato")

    fig_leads_nao_prosseguiram.update_traces(
        marker=dict(colors=["#dc3545", "#17a2b8"], line=dict(color='#2c3e50', width=1.5)),
        textinfo="percent+label",
        hoverinfo="label+percent",
        pull=[0.1, 0]
    )
    fig_leads_nao_prosseguiram.update_layout(
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Gráfico 7: Motivo de Perda dos Leads Não Elegíveis
    motivo_perda = filtered_df[filtered_df['NÃO ELEGÍVEL'] == 1]['lost_reason'].value_counts()

    fig_motivos_perda_leads = px.bar(x=motivo_perda.index, y=motivo_perda.values,
                                     title="Motivo de Perda dos Leads Não Elegíveis",
                                     labels={'x': 'Motivo', 'y': 'Número de Leads Não Elegíveis'})

    fig_motivos_perda_leads.update_traces(marker=dict(color='#ff5733', line=dict(color='#2c3e50', width=1.5)),
                                          opacity=0.85)
    fig_motivos_perda_leads.update_layout(
        plot_bgcolor="white",
        bargap=0.3,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_tickangle=-45
    )

    # Gráfico 8: Leads por Status (New Graph) 
    status_columns = ['LEAD 1', 'LEAD 2', 'LEAD 3', 'NÃO ELEGÍVEL', 'ClienteDesistiu']
    leads_by_status = filtered_df[status_columns].sum().sort_values(ascending=False)  # Sort in descending order
    fig_leads_status = px.bar(x=leads_by_status.index, y=leads_by_status.values,
                              title="Leads por Status",
                              labels={'x': 'Status', 'y': 'Número de Leads'})

    fig_leads_status.update_traces(marker_color="#007bff", marker_line_color="#2c3e50", marker_line_width=1.5)
    fig_leads_status.update_layout(
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        bargap=0.2
    )

    # Layout with cards placed beside graphs and ensuring responsiveness
    layout = dbc.Container([
        # First row: Total Leads graph with two cards to the right
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_total_leads), width=8),
            dbc.Col([
                card_total_pessoas,
                card_media_pessoas_dia
            ], width=4)
        ], align="center"),

        # Second row: Contracts signed graph with one card to the right
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_contratos_tempo), width=8),
            dbc.Col(card_contratos_assinados, width=4)
        ], align="center"),

        # Third row: Other graphs
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_leads_problema), width=6),  # Excluded from filter
            dbc.Col(dcc.Graph(figure=fig_leads_ddd), width=6),
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_fluxo_completo), width=6),
            dbc.Col(dcc.Graph(figure=fig_leads_nao_prosseguiram), width=6),
        ]),

        # Final row: Lead loss reasons and new Leads by Status graph
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_motivos_perda_leads), width=6),
            dbc.Col(dcc.Graph(figure=fig_leads_status), width=6),
        ]),
    ], fluid=True)

    return layout

# Callback to handle the date range picker and update Atendentes graphs
@app.callback(
    Output("atendentes-content", "children"),
    [Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date"),
     Input("problem-filter", "value")]
)
def update_atendentes_content(start_date, end_date, selected_problem):
    # Convert the date range values to datetime
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    else:
        start_date = df_merged['Data Inscrição'].min()
        end_date = df_merged['Data Inscrição'].max()

    # Filter the DataFrame based on the selected date range
    filtered_df = df_merged[(df_merged['Data Inscrição'] >= start_date) &
                            (df_merged['Data Inscrição'] <= end_date)]

    # Apply the problem filter if it's not "Nenhum"
    if selected_problem != "Nenhum":
        filtered_df = filtered_df[filtered_df[selected_problem] > 0]

    if filtered_df.empty:
        return html.Div("Nenhum dado disponível para o intervalo selecionado.")

    # Gráfico 1: Atendimentos por Dia por Atendente
    filtered_df['Atendentes'] = filtered_df['Atribuidos'].map({1: 'Gabrielle', 2: 'Hermes Moriguchi'})
    atendimentos_por_dia = filtered_df.groupby([filtered_df['Data Inscrição'].dt.date, 'Atendentes']).size().reset_index(name='Atendimentos')
    fig_atendimentos_por_dia = px.line(atendimentos_por_dia,
                                       x='Data Inscrição',
                                       y='Atendimentos',
                                       color='Atendentes',
                                       title="Atendimentos Atribuídos Diariamente Para Cada Atendente",
                                       labels={'Data Inscrição': 'Data', 'Atendimentos': 'Número de Atendimentos'})

    fig_atendimentos_por_dia.update_traces(line=dict(width=1.5, dash="solid"))
    
    # Add numbers above the points
    fig_atendimentos_por_dia.add_scatter(
        x=atendimentos_por_dia['Data Inscrição'],
        y=atendimentos_por_dia['Atendimentos'],
        mode='markers+text',
        text=atendimentos_por_dia['Atendimentos'],
        textposition='top center',
        textfont=dict(size=10),
        showlegend=False
    )
    # Set x-axis to start and end at the actual data range
    fig_atendimentos_por_dia.update_layout(
        xaxis=dict(range=[atendimentos_por_dia['Data Inscrição'].min(), atendimentos_por_dia['Data Inscrição'].max()]),
        plot_bgcolor="light grey",
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        transition=dict(duration=500)
    )

    # Gráfico 2: Total de Interações com Leads por Atendente
    interacoes_por_lead = filtered_df['Atendentes'].value_counts()
    fig_interacoes_por_lead = px.bar(x=interacoes_por_lead.index, y=interacoes_por_lead.values,
                                     title="Total de Atribuições Para Cada Atendente",
                                     labels={'x': 'Atendente', 'y': 'Número de Leads'})

    fig_interacoes_por_lead.update_traces(marker=dict(color=['#6f42c1', '#FFFF00'],
                                                      line=dict(color='white', width=2)),
                                          opacity=0.85, marker_line_width=2)
    fig_interacoes_por_lead.update_layout(
        plot_bgcolor="white",
        bargap=0.2,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_tickangle=-45
    )

    # Gráfico 3: Contratos Fechados por Atendente
    total_contratos_gabi = filtered_df[(filtered_df['Atribuidos'] == 1) & (filtered_df['Contrato'] == 1)].shape[0]
    total_contratos_hermes = filtered_df[(filtered_df['Atribuidos'] == 2) & (filtered_df['Contrato'] == 2)].shape[0]

    fig_contratos_por_atendente = px.bar(x=['Gabrielle', 'Hermes Moriguchi'],
                                         y=[total_contratos_gabi, total_contratos_hermes],
                                         title="Contratos Fechados por Atendente",
                                         labels={'x': 'Atendente', 'y': 'Número de Contratos Fechados'})

    fig_contratos_por_atendente.update_traces(marker=dict(color=['#6f42c1', '#FFFF00'],
                                                          line=dict(color='white', width=1.5)),
                                              opacity=0.85, marker_line_width=2)
    fig_contratos_por_atendente.update_layout(
        plot_bgcolor="white",
        bargap=0.2,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Return all Atendentes graphs
    return html.Div([
        dcc.Graph(figure=fig_atendimentos_por_dia, animate=True),
        dcc.Graph(figure=fig_interacoes_por_lead, animate=True),
        dcc.Graph(figure=fig_contratos_por_atendente, animate=True)
    ])

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8080)
