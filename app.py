import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados
file_path = 'base.xlsx'  # Certifique-se de que o arquivo esteja na mesma pasta
base_df = pd.read_excel(file_path, sheet_name='base')

# Título da aplicação
st.title('Quantitativos de Servidores por Secretarias e Cargos')

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

# Agrupar por cargo e ano dentro da secretaria selecionada e no intervalo de anos
cargo_ano_df = filtered_df.groupby(['Ano', 'Descrição_Cargo']).size().unstack(fill_value=0)

# Remover cargos com valor 0 para não aparecerem no gráfico
cargo_ano_df = cargo_ano_df.loc[:, (cargo_ano_df != 0).any(axis=0)]

# Calcular o somatório de servidores por ano
total_por_ano = cargo_ano_df.sum(axis=1)

# Plotar o gráfico de barras agrupadas dentro da secretaria selecionada e intervalo de anos
st.subheader(f'Servidores por Cargo na {selected_secretaria} ({ano_inicial}-{ano_final})')
fig, ax = plt.subplots(figsize=(12, 8))
cargo_ano_df.plot(kind='bar', stacked=True, ax=ax)  # Barras agrupadas e empilhadas

# Personalizar o gráfico
ax.set_title('Número de Servidores', fontsize=13)  # título
ax.set_xlabel('Anos', fontsize=13)  # Etiqueta do eixo x com tamanho maior
ax.set_ylabel('')  # Etiqueta do eixo y com tamanho maior
ax.legend(title='Legenda dos Cargos', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=4, fontsize=10)  # Legenda na parte inferior

# Adicionar o somatório no rótulo de cada barra
for i, total in enumerate(total_por_ano):
    ax.text(i, total, f"{total:,.0f}".replace(',', '.'), ha='center', va='bottom', fontsize=12, fontweight='bold')

# Aumentar o tamanho dos rótulos dos eixos
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=False) # Ocultar as marcações do eixo y

st.pyplot(fig)

# Preparar os dados detalhados para a tabela
dados_detalhados = filtered_df.groupby(['Descrição_Cargo', 'Cargo', 'Ano']).size().unstack(fill_value=0).reset_index()

# Renomear as colunas
dados_detalhados = dados_detalhados.rename(columns={'Descrição_Cargo': 'Descrição', 'Cargo': 'Código'})

# Formatar números na tabela com separador de milhar
dados_detalhados = dados_detalhados.applymap(lambda x: f"{x:,.0f}".replace(',', '.') if isinstance(x, (int, float)) else x)
# Exibir os dados detalhados em uma tabela
st.subheader(f'Dados Detalhados dos Cargos na {selected_secretaria} ({ano_inicial}-{ano_final})')
st.dataframe(dados_detalhados)
