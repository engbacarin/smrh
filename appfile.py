import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar a sidebar para navegação entre as páginas
st.sidebar.title("Navegação")
pagina_selecionada = st.sidebar.radio("Escolha a página", ["Análise Geral", "Análise por Cargo", "Análise por Secretaria"])

# Função para carregar o arquivo Excel com cache para melhorar performance
@st.cache_data
def carregar_dados(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name='base')
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
        return None

def calcular_variacao_oscilacao_generica(df, ano_inicial, ano_final, group_by_cols):
    # Agrupar os dados e reorganizar as colunas para que os anos sejam as colunas
    df_agrupado = df.groupby(group_by_cols + ['Ano']).size().unstack(fill_value=0).reset_index()

    # Calcular a variação entre o ano final e o ano inicial
    df_agrupado['Variação'] = df_agrupado[ano_final] - df_agrupado[ano_inicial]
    
    # Selecionar todas as colunas que representam os anos, exceto o ano final
    anos_para_oscilacao = [col for col in df_agrupado.columns if col not in group_by_cols + ['Ano', ano_final]]
    
    # Calcular a oscilação como a diferença entre o ano final e o valor máximo dos anos anteriores
    df_agrupado['Oscilação'] = df_agrupado[ano_final] - df_agrupado[anos_para_oscilacao].max(axis=1)
    
    return df_agrupado

# Função para selecionar anos e filtrar dados
def filtrar_dados(df):
    anos = sorted(df['Ano'].unique())
    col1, col2 = st.columns(2)
    
    with col1:
        ano_inicial = st.selectbox("Ano Inicial:", anos, index=0)
    with col2:
        ano_final = st.selectbox("Ano Final:", anos, index=len(anos) - 1)

    df_filtrado = df[(df['Ano'] >= ano_inicial) & (df['Ano'] <= ano_final)]
    return df_filtrado, ano_inicial, ano_final

# Função para exibir gráficos de Variação e Oscilação
def exibir_graficos_variacao_oscilacao(df_agrupado, tipo_analise):
    top_10_neg_var = df_agrupado.nsmallest(10, 'Variação')
    top_10_neg_osc = df_agrupado.nsmallest(10, 'Oscilação')

    if tipo_analise == 'Secretaria':
        titulo_variacao = "Secretarias com Maiores Redução"
        titulo_oscilacao = "Oscilação Máxima"
    else:
        titulo_variacao = "Cargos com Maiores Redução"
        titulo_oscilacao = "Oscilação Máxima"

    fig_top_10_variacao = px.bar(top_10_neg_var, x='Variação', y=top_10_neg_var.columns[0],
                                 orientation='h',
                                 title=titulo_variacao,
                                 labels={'Variação': 'Variação'})

    fig_top_10_oscilacao = px.bar(top_10_neg_osc, x='Oscilação', y=top_10_neg_osc.columns[0],
                                  orientation='h',
                                  title=titulo_oscilacao,
                                  labels={'Oscilação': 'Oscilação Máxima'})

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_top_10_variacao)
    with col2:
        st.plotly_chart(fig_top_10_oscilacao)

# Função para exibir a página "Análise Geral"
def pagina_analise_geral(df):
    st.title("Panorama Geral de Servidores")

    df_filtrado, ano_inicial, ano_final = filtrar_dados(df)
    panorama_geral = calcular_variacao_oscilacao_generica(df_filtrado, ano_inicial, ano_final, ['Secretaria'])

    exibir_graficos_variacao_oscilacao(panorama_geral, 'Secretaria')

    st.subheader('Quantidades de Servidores por Secretaria')
    st.dataframe(panorama_geral.style.set_properties(**{'text-align': 'center'}), height=400, use_container_width=True)

# Função para exibir a página "Análise por Cargo"
def pagina_analise_cargo(df):
    st.title("Panorama Geral de Servidores por Cargo")

    df_filtrado, ano_inicial, ano_final = filtrar_dados(df)
    panorama_cargo = calcular_variacao_oscilacao_generica(df_filtrado, ano_inicial, ano_final, ['Cargo', 'Descrição_Cargo'])

    exibir_graficos_variacao_oscilacao(panorama_cargo, 'Cargo')

    st.subheader('Quantidades de Servidores por Cargo')
    st.dataframe(panorama_cargo.style.set_properties(**{'text-align': 'center'}), height=400, use_container_width=True)

# Função para exibir a página "Quadro Funcional por Secretaria"
def pagina_analise_secretaria(df):
    st.title("Quadro Funcional por Secretaria")

    # Container com multiselect de Secretaria e seleção de anos
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            secretarias = st.multiselect("Selecione as Secretarias:", options=df['Secretaria'].unique())
        with col2:
            ano_inicial = st.selectbox("Ano Inicial:", sorted(df['Ano'].unique()), index=0)
        with col3:
            ano_final = st.selectbox("Ano Final:", sorted(df['Ano'].unique()), index=len(sorted(df['Ano'].unique())) - 1)

    if secretarias:
        # Filtrar os dados
        df_filtrado = df[(df['Secretaria'].isin(secretarias)) & (df['Ano'] >= ano_inicial) & (df['Ano'] <= ano_final)]

        # Agrupar os dados por Cargo, Descrição_Cargo e Ano
        panorama_secretaria = df_filtrado.groupby(['Cargo', 'Descrição_Cargo', 'Ano']).size().unstack(fill_value=0).reset_index()

        # Calcular Variação e Oscilação
        panorama_secretaria['Variação'] = panorama_secretaria[ano_final] - panorama_secretaria[ano_inicial]
        panorama_secretaria['Oscilação'] = panorama_secretaria[ano_final] - panorama_secretaria.iloc[:, 2:].max(axis=1)

        # Adicionar uma linha de soma na tabela
        sum_row = pd.DataFrame(panorama_secretaria.iloc[:, 2:].sum()).T
        sum_row['Cargo'] = 'Total'
        sum_row['Descrição_Cargo'] = ''
        panorama_secretaria = pd.concat([panorama_secretaria, sum_row], ignore_index=True)

        # Gráfico de Barras Agrupadas
        fig_barras_agrupadas = px.bar(panorama_secretaria[:-1], x='Cargo', y=list(range(ano_inicial, ano_final+1)),
                                      title="Distribuição de Servidores por Secretaria",
                                      labels={'value': 'Quantidade de Servidores', 'variable': 'Ano'})

        st.plotly_chart(fig_barras_agrupadas)

        # Exibir a tabela com as contagens e variações
        st.subheader('Distribuição de Servidores por Secretaria')
        st.dataframe(panorama_secretaria.style.set_properties(**{'text-align': 'center'}), height=400, use_container_width=True)
    else:
        st.warning("Selecione uma ou mais secretarias para ver as informações.")

# Upload do arquivo Excel
uploaded_file = st.sidebar.file_uploader("Faça o upload da base de dados (.xlsx)", type=["xlsx"], help="Arraste e solte o arquivo aqui ou clique para selecionar.")

# Carregar os dados se o arquivo foi enviado
if uploaded_file is not None:
    with st.spinner('Carregando dados...'):
        df = carregar_dados(uploaded_file)

    if df is not None:
        # Verificar qual página foi selecionada e chamar a função correspondente
        if pagina_selecionada == "Análise Geral":
            pagina_analise_geral(df)
        elif pagina_selecionada == "Análise por Cargo":
            pagina_analise_cargo(df)
        elif pagina_selecionada == "Análise por Secretaria":
            pagina_analise_secretaria(df)
else:
    st.sidebar.warning("Por favor, faça o upload de um arquivo Excel (.xlsx) para continuar.")
