# -*- coding: utf-8 -*-
"""estrutura.ipynb

# Puxando os dados do Analytics
"""

# !pip install google-analytics-data
# !pip install dash dash-bootstrap-components plotly flask

from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, DateRange, Dimension, Metric
import requests
from datetime import datetime, timedelta
from flask import Flask
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

"""# Puxando os dados da API do Pipedrive"""

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

# Selecionar uma linha aleatória
random_row = df_pipedrive.sample(n=1)  # Seleciona uma linha aleatória

# Exibir os valores da linha selecionada
print("Exemplo de uma linha aleatória:")
print(random_row)

# Exibir um exemplo de cada coluna
print("\nExemplo de cada coluna da linha aleatória:")
for column in random_row.columns:
    print(f"{column}: {random_row[column].values[0]}")

"""# Puxando as etiquetas"""

# Carregar o arquivo etiquetas.xlsx
df_etiquetas = pd.read_excel('etiquetas.xlsx')

# Substituir valores nulos por 0
df_etiquetas = df_etiquetas.fillna(0)

# Salvar como CSV
df_etiquetas.to_csv('etiquetas.csv', index=False)
print("Arquivo etiquetas.xlsx convertido para etiquetas.csv com sucesso e valores nulos substituídos por 0.")

# Carregar o arquivo etiquetas.xlsx
df_etiquetas = pd.read_excel('etiquetas.xlsx')

# Substituir valores nulos e valores não numéricos por 0
df_etiquetas = df_etiquetas.apply(pd.to_numeric, errors='coerce').fillna(0)

# Converter colunas numéricas de float para int
df_etiquetas = df_etiquetas.astype(int)

# Renomear a coluna 'telefone' para 'numero_wpp'
df_etiquetas = df_etiquetas.rename(columns={'Telefone': 'numero_wpp'})

# Adicionar um '+' antes de todos os valores na coluna 'numero_wpp'
df_etiquetas['numero_wpp'] = df_etiquetas['numero_wpp'].apply(lambda x: f'+{x}')

# Salvar como CSV
df_etiquetas.to_csv('etiquetas.csv', index=False)
print("Arquivo etiquetas.xlsx convertido para etiquetas.csv com sucesso, valores nulos substituídos por 0, colunas numéricas convertidas para int, e coluna 'telefone' renomeada para 'numero_wpp'.")

"""# Puxando os dados do endpoint"""

# Função para buscar todos os dados do endpoint
def fetch_all_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)  # Converte os dados em um DataFrame
        else:
            print(f"Error: {response.status_code}, Detail: {response.json().get('detail', 'No detail provided')}")
    except requests.RequestException as e:
        print(f"Failed to make the request: {e}")
        return pd.DataFrame()

# URL do endpoint
url = "https://web-production-c353.up.railway.app/retrieve_all"

# Chamando a função e obtendo os dados
df_endpoint = fetch_all_data(url)

# Verificação básica dos dados
if df_endpoint.empty:
    print("Os dados não foram carregados corretamente. Verifique o endpoint ou o formato dos dados.")
    exit()

# Função para calcular o tempo em cada etapa com base nas colunas de timestamp
def calculate_stage_duration(row):
    created_at = pd.to_datetime(row['created_at'], errors='coerce')
    last_modified = pd.to_datetime(row['last_modified'], errors='coerce')
    if pd.isnull(created_at) or pd.isnull(last_modified):
        return 0  # Retorna 0 se houver erro de conversão
    duration = (last_modified - created_at).total_seconds() / 60  # Duração em minutos
    return duration

# Função para extrair a última etapa (flag) alcançada na jornada
def extract_final_stage(raw_data):
    try:
        flags = {
            'voo': int(raw_data.get('FLAG_VOO_JORNADA', 0)),
            'negativacao': int(raw_data.get('FLAG_NEGATIVACAO_JORNADA', 0)),
            'telefonia': int(raw_data.get('FLAG_SERV_TELEF_JORNADA', 0)),
            'bancario': int(raw_data.get('FLAG_SERV_BANCARIO_JORNADA', 0)),
            'compra_online': int(raw_data.get('FLAG_COMPRA_ONLINE_JORNADA', 0)),
            'outros': int(raw_data.get('FLAG_OUTROS_JORNADA', 0)),
            'hospedagem': int(raw_data.get('FLAG_HOSPEDAGEM_JORNADA', 0))
        }
        final_stage = max(flags.values())  # Encontra a maior flag para determinar a etapa final
        return final_stage
    except Exception as e:
        print(f"Erro ao extrair etapa final: {e}")
        return 0

# Aplicar as funções ao dataframe
df_endpoint['created_at'] = pd.to_datetime(df_endpoint['created_at'], errors='coerce')
df_endpoint['Tempo_na_Etapa'] = df_endpoint.apply(calculate_stage_duration, axis=1)
df_endpoint['Etapa_Final'] = df_endpoint['RAW_DATA'].apply(extract_final_stage)

# Substituir valores NaN por 0 em todas as colunas do df_endpoint
df_endpoint = df_endpoint.fillna(0)

# Criar a coluna FLAG_FINAL, onde 1 indica que a pessoa chegou ao fim e 0 indica que não
df_endpoint['FLAG_FINAL'] = df_endpoint[['FLAG_VOO_JORNADA', 'FLAG_NEGATIVACAO_JORNADA', 'FLAG_SERV_TELEF_JORNADA',
                                         'FLAG_SERV_BANCARIO_JORNADA', 'FLAG_COMPRA_ONLINE_JORNADA', 'FLAG_OUTROS_JORNADA',
                                         'FLAG_HOSPEDAGEM_JORNADA']].max(axis=1).apply(lambda x: 1 if x > 0 else 0)

# Exibir as primeiras linhas para ver o resultado
print(df_endpoint[['FLAG_FINAL', 'created_at', 'Tempo_na_Etapa']].head())

"""# Unificação e tratamento de dados"""

# Duplicar os DataFrames
df_endpoint_dup = df_endpoint.copy()
df_pipedrive_dup = df_pipedrive.copy()
df_etiquetas_dup = df_etiquetas.copy()

# Quebrar a coluna 'title' no df_pipedrive_dup em três colunas
df_pipedrive_dup[['id2', 'Problema2', 'numero_wpp']] = df_pipedrive_dup['title'].str.extract(r'(\d+)\s*-\s*(.*?)\s*-\s*(\+\d+)')

# Remover a coluna original 'title' depois de extrair os valores
df_pipedrive_dup.drop('title', axis=1, inplace=True)

# Passo 1: Remover duplicatas no numero_wpp para evitar dados inconsistentes
df_endpoint_dup_clean = df_endpoint_dup.drop_duplicates(subset='numero_wpp')
df_pipedrive_dup_clean = df_pipedrive_dup.drop_duplicates(subset='numero_wpp')

# Passo 2: Realizar o merge com base no numero_wpp (inner join para manter apenas os números em comum)
df_merged = pd.merge(df_pipedrive_dup_clean, df_endpoint_dup_clean, on='numero_wpp', how='inner', suffixes=('_pipedrive', '_endpoint'))

# Reorganizar as colunas para que 'numero_wpp' seja a primeira
cols = ['numero_wpp'] + [col for col in df_merged.columns if col != 'numero_wpp']
df_merged = df_merged[cols]

# Salvar o dataframe unificado para uso posterior
df_final = pd.merge(df_merged, df_etiquetas_dup, on='numero_wpp', how='left')

# Remover todas as linhas onde o valor na coluna 'POSSÍVEL' seja NaN
df_final_limpo = df_final.dropna(subset=['POSSÍVEL'])

"""# Dashboard com Dash"""

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Estilos personalizados
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "20px",
    "background-color": "#343a40",  # Cor da barra lateral (cinza escuro)
}

CONTENT_STYLE = {
    "margin-left": "20%",
    "padding": "20px",
    "background-color": "#f8f9fa",  # Cor da parte central/direita (cinza claro)
    "text-align": "center"  # Centralizar o texto
}

# Layout da barra lateral
sidebar = html.Div(
    [
        html.H2("Dashboard", className="display-6", style={"color": "white"}),
        html.Hr(),
        html.P("Solucionaí", className="lead", style={"color": "white"}),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", id="home-button", style={"color": "white"}),
                dbc.NavLink("Leads", href="/leads", id="leads-button", style={"color": "white"}),
                dbc.NavLink("Análise detalhada de leads", href="/analise-leads", id="analise-leads-button", style={"color": "white"}),
                dbc.NavLink("Atendentes", href="/atendentes", id="atendentes-button", style={"color": "white"}),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Layout da parte central/direita
content = html.Div(
    [
        html.H2("Dashboard de Dados Solucionaí", className="display-4"),
        html.Hr(),
        html.Div(id="page-content"),
    ],
    style=CONTENT_STYLE,
)

# Layout principal combinando a barra lateral e o conteúdo
app.layout = html.Div([sidebar, content])

# Callback para atualizar o conteúdo da página
@app.callback(
    Output("page-content", "children"),
    [Input("home-button", "n_clicks"),
     Input("leads-button", "n_clicks"),
     Input("analise-leads-button", "n_clicks"),
     Input("atendentes-button", "n_clicks")]
)
def display_page(n_home, n_leads, n_analise, n_atendentes):
    ctx = dash.callback_context  # Verificar qual botão foi clicado
    if not ctx.triggered:
        return html.H3("Home, seja bem-vindo ao Dashboard de Dados da Solucionaí!")
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "home-button":
            return html.H3("Home, seja bem-vindo ao Dashboard de Dados da Solucionaí!")
        elif button_id == "leads-button":
            try:
                dropdown_problema = dcc.Dropdown(
                    id='problema-dropdown',
                    options=[{'label': problema, 'value': problema} for problema in df_final_limpo['PROBLEMA'].unique()],
                    value=df_final_limpo['PROBLEMA'].unique()[0] if not df_final_limpo.empty else None,
                    clearable=False,
                    style={'width': '50%', 'margin-bottom': '20px'}
                )

                leads_by_date = df_final_limpo.groupby(df_final_limpo['created_at'].dt.date).size()
                fig_total_leads = px.line(x=leads_by_date.index, y=leads_by_date.values, title="Total de Leads por Período",
                                          labels={'x': 'Data', 'y': 'Número de Leads'})

                leads_by_problem = df_final_limpo['PROBLEMA'].value_counts()
                fig_leads_problema = px.bar(x=leads_by_problem.index, y=leads_by_problem.values, title="Leads por Tipo de Problema",
                                            labels={'x': 'Tipo de Problema', 'y': 'Contagem de Leads'})

                leads_by_ddd = df_final_limpo['Estado'].value_counts()
                leads_by_ddd = leads_by_ddd[leads_by_ddd > 1]  # Filtrar para exibir apenas os valores maiores que 1
                fig_leads_ddd = px.bar(x=leads_by_ddd.index, y=leads_by_ddd.values, title="Leads por Região",
                                       labels={'x': 'Estado', 'y': 'Contagem de Leads'})

                completed_flow = df_final_limpo[df_final_limpo['FLAG_FINAL'] == 1].shape[0]
                fig_fluxo_completo = px.pie(values=[completed_flow, df_final_limpo.shape[0] - completed_flow],
                                            names=['Completaram', 'Não Completaram'],
                                            title="Leads que Completaram o Fluxo até o Final")

                return html.Div([
                    dropdown_problema,
                    dcc.Graph(figure=fig_total_leads),
                    html.Div(id="leads-info", style={'text-align': 'center', 'margin': '20px 0'}),
                    dcc.Graph(figure=fig_leads_problema),
                    dcc.Graph(figure=fig_leads_ddd),
                    dcc.Graph(figure=fig_fluxo_completo),
                    dcc.Graph(id="tempo-por-lead-wpp-graph")
                ])
            except Exception as e:
                return html.Div(f"Erro ao carregar os dados: {str(e)}")

# Callback para o gráfico de tempo na etapa por número de WhatsApp com filtro por problema
@app.callback(
    [Output('tempo-por-lead-wpp-graph', 'figure'),
     Output('leads-info', 'children')],
    [Input('problema-dropdown', 'value')]
)
def update_tempo_por_lead_graph(selected_problema):
    df_filtered_by_problem = df_final_limpo[df_final_limpo['PROBLEMA'] == selected_problema]

    df_filtered = df_filtered_by_problem[(df_filtered_by_problem['Tempo_na_Etapa'] <= 40) &
                                         (df_filtered_by_problem['Tempo_na_Etapa'] > 0)]

    fig_tempo_por_lead_wpp = px.bar(
        df_filtered,
        x='numero_wpp',
        y='Tempo_na_Etapa',
        title='Tempo na Etapa por Lead (Filtrado)',
        labels={'Tempo_na_Etapa': 'Tempo na Etapa (minutos)', 'numero_wpp': 'Número WhatsApp'},
        hover_data={'Etapa_Final': True}
    )

    leads_captados_total = len(df_final_limpo['numero_wpp'].unique())
    leads_captados = len(df_filtered_by_problem['numero_wpp'].unique())
    proporcao_responderam = (leads_captados / leads_captados_total * 100) if leads_captados_total > 0 else 0

    leads_info = [
        html.H4(f"Leads Captados no Problema Selecionado: {leads_captados}"),
        html.H4(f"Total de Leads Captados: {leads_captados_total}"),
        html.H4(f"Proporção de Leads no Problema Selecionado: {proporcao_responderam:.2f}%")
    ]

    return fig_tempo_por_lead_wpp, leads_info

# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=False)
