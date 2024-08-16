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
    cargo_ano_df = filtered_df.groupby(['Ano', 'Descrição']).size().unstack(fill_value=0)

    # Remover cargos com valor 0 para não aparecerem no gráfico
    cargo_ano_df = cargo_ano_df.loc[:, (cargo_ano_df != 0).any(axis=0)]

    # Calcular o somatório de servidores por ano
    total_por_ano = cargo_ano_df.sum(axis=1)

    # Plotar o gráfico de barras agrupadas dentro da secretaria selecionada e intervalo de anos
    st.subheader(f'Servidores por Cargo na {selected_secretaria} ({ano_inicial}-{ano_final})')
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = cargo_ano_df.plot(kind='bar', stacked=True, ax=ax)  # Barras agrupadas e empilhadas

    # Adicionar o somatório no rótulo de cada barra
    for i, total in enumerate(total_por_ano):
        ax.text(i, total, f"{total:,.0f}".replace(',', '.'), ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Personalizar o gráfico
    ax.set_title('')  # Omitir o título
    ax.set_xlabel('Ano', fontsize=12)  # Etiqueta do eixo x com tamanho maior
    ax.set_ylabel('')  # Omitir o eixo y
    ax.legend(title='Legenda dos Cargos', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=4, fontsize=10)  # Legenda na parte inferior

    # Aumentar o tamanho dos rótulos dos eixos
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', left=False)  # Ocultar as marcações do eixo y

    st.pyplot(fig)

    # Preparar os dados detalhados para a tabela
    dados_detalhados = filtered_df.groupby(['Descrição', 'Código', 'Ano']).size().unstack(fill_value=0).reset_index()

    # Formatar números na tabela com separador de milhar
    dados_detalhados = dados_detalhados.applymap(lambda x: f"{x:,.0f}".replace(',', '.') if isinstance(x, (int, float)) else x)

    # Exibir os dados detalhados em uma tabela
    st.subheader(f'Dados Detalhados: {selected_secretaria} ({ano_inicial}-{ano_final})')
    st.dataframe(dados_detalhados)
else:
    st.warning("Por favor, faça o upload de um arquivo Excel (.xlsx) para continuar. Arraste ou clique para selecionar.")