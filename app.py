import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título da aplicação
st.title('Quantitativos de Servidores por Secretaria')

# Carregar os dados do arquivo Excel (base.xlsx)
base_df = pd.read_excel("base.xlsx", sheet_name='base')

# Criar um container para as seleções, exibindo lado a lado
st.subheader('Selecione os Parâmetros')
col1, col2, col3 = st.columns(3)

with col1:
    # Selecionar uma secretaria e organizar em ordem alfabética
    secretarias = sorted(base_df['Secretaria'].unique().tolist())
    selected_secretaria = st.selectbox("Escolha uma Secretaria:",[Nenhuma]+secretarias)

with col2:
    # Selecionar o ano inicial
    anos = sorted(base_df['Ano'].unique())
    ano_inicial = st.selectbox("Ano Inicial:", anos, index=0)

with col3:
    # Selecionar o ano final
    ano_final = st.selectbox("Ano Final:", anos, index=len(anos) - 1)
# Verificar se alguma secretaria foi selecionada
if selected_secretaria != "Nenhuma":
    
    # Filtrar os dados para a secretaria selecionada e dentro do intervalo de anos
    filtered_df = base_df[
        (base_df['Secretaria'] == selected_secretaria) &
        (base_df['Ano'] >= ano_inicial) &
        (base_df['Ano'] <= ano_final)
    ]

    # Renomear as colunas antes de agrupar
    filtered_df = filtered_df.rename(columns={'Cargo': 'Código', 'Descrição_Cargo': 'Descrição'})

    # Plotar o gráfico de barras agrupadas dentro da secretaria selecionada e intervalo de anos
    st.subheader(f'Quantidade de Servidores na {selected_secretaria} ({ano_inicial}-{ano_final})')
    fig, ax = plt.subplots(figsize=(12, 8))
    cargo_ano_df = filtered_df.groupby(['Ano', 'Descrição']).size().unstack(fill_value=0)
    bars = cargo_ano_df.plot(kind='bar', stacked=True, ax=ax)  # Barras agrupadas e empilhadas

    # Adicionar o somatório no rótulo de cada barra
    total_por_ano = cargo_ano_df.sum(axis=1)
    for i, total in enumerate(total_por_ano):
        ax.text(i, total, f"{total:,.0f}".replace(',', '.'), ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Personalizar o gráfico
    ax.set_title('')  # Omitir o título
    ax.set_xlabel('ANO', fontsize=12)  # Etiqueta do eixo x com tamanho maior
    ax.set_ylabel('')  # Omitir o eixo y
    ax.legend(title='LEGENDA', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=4, fontsize=10)  # Legenda na parte inferior

    # Aumentar o tamanho dos rótulos dos eixos
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', left=False)  # Ocultar as marcações do eixo y

    st.pyplot(fig)

    # Agrupar por cargo e ano dentro da secretaria selecionada e no intervalo de anos
    dados_detalhados = filtered_df.groupby(['Descrição', 'Código', 'Ano']).size().unstack(fill_value=0).reset_index()

   # Calcular a linha de totais para as colunas dos anos
    totais = dados_detalhados.iloc[:, 2:].sum()
    totais_row = pd.DataFrame(totais).T
    totais_row.insert(0, 'Descrição', 'TOTAL')
    totais_row.insert(1, 'Código', '')

    # Adicionar a linha de totais ao DataFrame
    dados_detalhados = pd.concat([dados_detalhados, totais_row], ignore_index=True)

    # Remover o índice na última linha
    dados_detalhados.index = dados_detalhados.index.map(str)  # Converter índice para string
    dados_detalhados.index = dados_detalhados.index[:-1].tolist() + ['']  # Omitir o índice da última linha

    # Formatar números na tabela com separador de milhar
    dados_detalhados = dados_detalhados.applymap(lambda x: f"{x:,.0f}".replace(',', '.') if isinstance(x, (int, float)) else x)

    # Exibir os dados detalhados em uma tabela
    st.subheader(f'Dados Detalhados dos Cargos lotados na: {selected_secretaria} ({ano_inicial}-{ano_final})')
    st.dataframe(dados_detalhados.style.set_properties(**{'text-align': 'center'}))
else:
    st.warning("Por favor, selecione uma Secretaria para visualizar os dados.")
