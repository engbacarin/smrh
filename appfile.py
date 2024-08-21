import streamlit as st
import pandas as pd

# Título da aplicação
st.title('Quantitativos de Servidores por Secretaria')

# Upload do arquivo Excel ou CSV
uploaded_file = st.file_uploader("Faça o upload da base de dados (.xlsx ou .csv)", type=["xlsx", "csv"], help="Arraste e solte o arquivo aqui ou clique para selecionar.")

if uploaded_file is not None:
    try:
        # Carregar os dados do arquivo (detectar se é Excel ou CSV)
        if uploaded_file.name.endswith('.xlsx'):
            base_df = pd.read_excel(uploaded_file, sheet_name='base')
        elif uploaded_file.name.endswith('.csv'):
            base_df = pd.read_csv(uploaded_file)

        # Verifica se as colunas necessárias estão no arquivo
        if not all(col in base_df.columns for col in ['Secretaria', 'Ano', 'Cargo', 'Descrição_Cargo']):
            st.error("O arquivo deve conter as colunas: 'Secretaria', 'Ano', 'Cargo', 'Descrição_Cargo'")
        else:
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

            # Converter colunas de ano para tipo numérico (inteiro)
            dados_detalhados.iloc[:, 2:] = dados_detalhados.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')

            # Calcular a diferença ano a ano e somar as diferenças
            for i in range(2, len(dados_detalhados.columns) - 1):
                dados_detalhados[f'Dif_{dados_detalhados.columns[i+1]}'] = dados_detalhados.iloc[:, i+1] - dados_detalhados.iloc[:, i]

            # Calcular o somatório das diferenças anuais (diminuições no quadro funcional)
            dados_detalhados['Maior_Decréscimo'] = dados_detalhados.filter(like='Dif_').sum(axis=1)

            # Ordenar os cargos que tiveram maior diminuição no quadro funcional
            dados_detalhados = dados_detalhados.sort_values(by='Maior_Decréscimo')

            # Exibir os dados detalhados e a análise de decréscimo
            st.subheader(f'Dados Detalhados dos Cargos lotados na: {selected_secretaria} ({ano_inicial}-{ano_final})')
            st.dataframe(dados_detalhados.style.set_properties(**{'text-align': 'center'}))

            # Exibir os cargos com maior decréscimo no quadro funcional
            st.subheader(f'Cargos com Maior Decréscimo no Quadro Funcional ({ano_inicial}-{ano_final})')
            st.dataframe(dados_detalhados[['Descrição', 'Código', 'Maior_Decréscimo']].style.set_properties(**{'text-align': 'center'}))

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.warning("Por favor, faça o upload de um arquivo Excel (.xlsx) ou CSV (.csv) para continuar. Arraste e solte o arquivo ou clique para selecionar.")
