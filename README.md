# Visão Geral
Este projeto implementa um dashboard interativo para monitorar leads e atendentes, fornecendo insights como leads por região, total de leads, total de contratos assinados, leads por dia, atendimentos por atendente, contratos assinados por atendente, entre outros. O dashboard é criado usando Dash e Plotly para visualizações dinâmicas, com dados extraídos das bases de dados do BotConversa.

# Bibliotecas Importadas
requests: Usado para fazer solicitações HTTP à API do Pipedrive. (a utilização dessa API foi descontinuada no projeto mas caso queira utilizar o código está pronto).

dash, dcc, html: Usados para a construção da interface do dashboard.

plotly.express: Utilizado para criar gráficos interativos.

pandas: Para manipulação de dados.

flask: Necessário para rodar o dashboard como um serviço web.

# Geração de Visualizações
Utilizamos Plotly Express para criar os gráficos.

# Estrutura do Dashboard
1. Pre-processamento dos Dados
Renomeação de Colunas: A coluna owner_name é renomeada para Atendentes para facilitar a visualização e a manipulação.

Conversão de Datas: A coluna Data Inscrição é convertida para o formato datetime para possibilitar cálculos de tempo.

Cálculos Estatísticos:
Calcula o total de leads, a diferença de dias entre o primeiro e o último registro de lead e a média de leads por dia.
Também calcula o total de contratos assinados.

3. Funções de Visualização
O código contém várias funções que criam gráficos interativos usando Plotly. Algumas delas incluem:

Gráfico de Atendimentos por Dia:

Gera um gráfico de barras que mostra o número de atendimentos realizados por dia para cada atendente.

Gráfico de Interações por Lead:

Exibe o número de interações realizadas com cada lead para cada atendente.
Usa cores distintas para cada atendente e ajusta o layout visual.

Gráfico de Contratos Fechados por Atendente:

Exibe a quantidade de contratos fechados por atendente, comparando o desempenho entre diferentes membros da equipe.
Gera um gráfico de barras com atendentes no eixo X e o número de contratos no eixo Y.

3. Estilos Personalizados dos Cards
O código define vários estilos de "cards" usados na interface do dashboard, com diferentes cores, tamanhos e bordas personalizadas. Esses cards são usados para exibir KPIs importantes, como o número de contratos assinados e a média de leads por dia.

4. Estrutura do Dashboard (Usando Dash)
Layout do Dashboard:
O dashboard é construído com o framework Dash, que usa dcc.Graph para gráficos interativos e html.Div para estruturar o layout.
Callback de Atualização:
O código utiliza callbacks do Dash para permitir que os gráficos sejam atualizados dinamicamente conforme os dados mudam.

5. Execução do Servidor
Função Principal:
A função principal inicializa o servidor Flask e abre o dashboard no endereço https://web-production-a7114.up.railway.app/home .
Usa o modo debug=True para facilitar o desenvolvimento, exibindo erros detalhados quando ocorrem.

# Passo a Passo para Configurar o Projeto
O projeto já está rodando automaticamente após o deploy no Railway. Para manter os dados atualizados, basta substituir as 5 bases de dados e seguir as instruções no arquivo 'instruções.txt'.

# Estrutura dos arquivos
├── estrutura.py                # Código principal do dashboard

├── gabi.xlsx                   # Base de dados relacionada ao total de casos atribuídos à Gabrielle.

├── hermes.xlsx                 # Base de dados relacionada ao total de casos atribuídos ao Hermes.

├── contratog.xlsx              # Dados de contratos totais assinados onde o caso foi atribuído à Gabrielle.

├── contratoh.xlsx              # Dados de contratos totais assinados onde o caso foi atribuído ao Hermes.

├── etiquetas.xlsx              # Base de dados que contém todas as leads e suas respectivas etiquetas.


# Railway
Caso queira fazer consultas ao local do deploy basta fazer login em https://railway.app com esse mesmo login e senha e escolher o projeto "beneficial-reverence", lá é onde nosso Dashboard foi colocado em produção.

# Considerações finais
O Dashboard está rodando e funcionando perfeitamente, se quiser fazer alguma alteração na estrutura do código está anexado também o arquivo ipynb, já caso a alteração desejada seja apenas uma atualização diária dos dados siga as instruções no arquivo 'instruções.txt'.
