# -*- coding: utf-8 -*-
"""estrutura.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SiAX_nByBZsXkuO4Ax5-vIOOPZL_vJDr

# Puxando os dados do Analytics
"""
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

# Lista de colunas de interesse
columns = [
    'FLAG_HOSPEDAGEM_JORNADA',
    'FLAG_OUTROS_JORNADA',
    'FLAG_VOO_JORNADA',
    'FLAG_COMPRA_ONLINE_JORNADA',
    'FLAG_SERV_BANCARIO_JORNADA',
    'FLAG_NEGATIVACAO_JORNADA',
    'FLAG_SERV_TELEF_JORNADA'
]

# Converter as colunas para numérico, ignorando erros e preenchendo com NaN para valores não convertíveis
for col in columns:
    df_endpoint[col] = pd.to_numeric(df_endpoint[col], errors='coerce')

# Calcular o valor máximo para cada coluna
max_values = {col: df_endpoint[col].max() for col in columns}

# Determinar o valor máximo global entre todas as flags
max_global = max(max_values.values())

print("Valores máximos de cada coluna:")
for col, max_val in max_values.items():
    print(f"{col}: {max_val}")

print(f"Valor máximo global: {max_global}")

# Criar a coluna FLAG_FINAL, onde 1 indica que a pessoa chegou ao fim e 0 indica que não
df_endpoint['FLAG_FINAL'] = df_endpoint[columns].max(axis=1).apply(lambda x: 1 if x == max_global else 0)

# # Exibir as primeiras linhas para ver o resultado
# print(df_endpoint[['FLAG_FINAL'] + columns].head())

"""# Unificação e tratamento de dados"""

# Duplicar os DataFrames
df_endpoint_dup = df_endpoint
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

solucionai.COMPARTILHADO01

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8080)
