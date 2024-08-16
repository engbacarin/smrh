import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título da aplicação
st.title('Quantitativos de Servidores por Secretaria e Cargo')

# Upload do arquivo Excel com texto em português
uploaded_file = st.file_uploader("Faça o upload da base de dados (.xlsx)", type="xlsx", help="Arraste ou clique para selecionar.")

if uploaded_file is not None:
    # Carregar os dados do arquivo Excel
    base_df = pd.read_excel(uploaded_file, sheet_name='base')

    # Criar um container para as seleções, exibindo lado a lado
    st.subheader('Selecione os Parâmetros')
    col1, col2, col3 = st.columns(3)

    with col1:
        # Selecionar uma secretaria e organizar em ordem alfabética
        secretarias = sorted(base_df['Secretaria'].unique().tolist())
        selected_secretaria = st.selectbox("Escolha uma Secretaria:", secretarias)

    with col2:
        # Selecionar o ano inicial
        anos = sorted(base_df['Ano'].unique())
        ano_inicial = st.selectbox("Ano Inicial:", anos, index=0)

    with col3:
        # Selecionar o ano final
        ano_final = st.selectbox("Ano Final:", anos, index=len(anos) - 1)

    # Filtrar os dados para a secretaria selecionada e dentro do intervalo de anos
    filtered_df = base_df[
        (base_df['Secretaria'] == selected_secretaria) &
        (base_df['Ano'] >= ano_inicial) &
        (base_df['Ano'] <= ano_final)
    ]

    # Renomear as colunas antes de agrupar
    filtered_df = filtered_df.rename(columns={'Cargo': 'Código', 'Descrição_Cargo': 'Descrição'})

    # Agrupar por cargo e ano dentro da secretaria selecionada e no intervalo de anos
    dados_detalhados = filtered_df.groupby(['Descrição', 'Código', 'Ano']).size().unstack(fill_value=0).reset_index()

    # Calcular a linha de totais
    totais = dados_detalhados.iloc[:, 2:].sum()
    totais_row = pd.DataFrame(totais).T
    totais_row.insert(1, 'Descrição', '')
    totais_row.insert(0, 'Código', 'TOTAL')

    # Adicionar a linha de totais ao DataFrame
    dados_detalhados = pd.concat([dados_detalhados, totais_row], ignore_index=True)

    # Formatar números na tabela com separador de milhar
    dados_detalhados = dados_detalhados.applymap(lambda x: f"{x:,.0f}".replace(',', '.') if isinstance(x, (int, float)) else x)

    # Exibir os dados detalhados em uma tabela
    st.subheader(f'Dados Detalhados dos Cargos na: {selected_secretaria} ({ano_inicial}-{ano_final})')
    st.dataframe(dados_detalhados)
else:
    st.warning("Por favor, faça o upload de um arquivo Excel (.xlsx) para continuar. Arraste e solte o arquivo ou clique para selecionar.")
