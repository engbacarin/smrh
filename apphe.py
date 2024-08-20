import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar título da página
st.set_page_config(page_title='Análise de Horas Extras Realizadas')

# Função para formatar números no padrão brasileiro
def format_number_brazilian(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Título da página
st.title('Análise de Horas Extras Realizadas')

# Solicitar o upload do arquivo Excel
uploaded_file = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Função para carregar os dados com cache
    @st.cache_data
    def load_data(file):
        # Carregar os dados da planilha
        data = pd.read_excel(file, sheet_name='base', usecols=['Ano', 'Matricula', 'Secretaria', 'Cod_Cargo', 'Cargo', 'Horas_realizadas'])
        # Converter a coluna 'Horas_realizadas' para numérico
        data['Horas_realizadas'] = pd.to_numeric(data['Horas_realizadas'], errors='coerce')
        return data

    # Carregar os dados uma única vez e armazenar em cache
    base_df = load_data(uploaded_file)

    # Filtros Interativos
    selected_years = st.multiselect('Selecione o(s) Ano(s)', base_df['Ano'].unique())
    selected_secretaria = st.multiselect('Selecione a Secretaria', base_df['Secretaria'].unique())

    # Verificação se o usuário selecionou ao menos um ano e uma secretaria
    if not selected_years and not selected_secretaria:
        st.warning('Por favor, selecione ao menos um ano e uma secretaria para visualizar os dados.')
    elif not selected_years:
        st.warning('Por favor, selecione ao menos um ano para visualizar os dados.')
    elif not selected_secretaria:
        st.warning('Por favor, selecione ao menos uma secretaria para visualizar os dados.')
    else:
        # Filtragem dos Dados
        filtered_data = base_df[(base_df['Ano'].isin(selected_years)) & (base_df['Secretaria'].isin(selected_secretaria))]

        # Agrupando por Cod_Cargo e somando as horas realizadas
        grouped_data = filtered_data.groupby(['Cod_Cargo', 'Cargo'])['Horas_realizadas'].sum().reset_index()

        # Ordenando os dados do maior para o menor
        grouped_data = grouped_data.sort_values(by='Horas_realizadas', ascending=False)

        # Exibir apenas os 10 primeiros cargos com maior soma de horas realizadas
        top_10_grouped_data = grouped_data.head(10)

        # Aplicando a formatação numérica manualmente na tabela
        grouped_data['Horas_realizadas'] = grouped_data['Horas_realizadas'].apply(format_number_brazilian)

        # Nome do gráfico dinâmico (subheader)
        titulo_grafico = f'Horas Extras realizadas na {", ".join(selected_secretaria)} em {", ".join(map(str, selected_years))}'
        st.subheader(titulo_grafico)

        # Criação do gráfico usando matplotlib sem título e sem notação científica no eixo Y
        fig, ax = plt.subplots()
        ax.bar(top_10_grouped_data['Cargo'], top_10_grouped_data['Horas_realizadas'])
        ax.set_xlabel('')
        ax.set_ylabel('Horas Extras')

        # Desativar notação científica no eixo Y
        ax.get_yaxis().get_major_formatter().set_scientific(False)

        # Rotacionar os rótulos do eixo X para melhor legibilidade
        plt.xticks(rotation=45, ha='right')

        # Exibir o gráfico no Streamlit
        st.pyplot(fig)

        # Exibição da Tabela de Dados Detalhados
        st.subheader('Detalhamento dos Dados')
        st.write(grouped_data)
else:
    st.info("Por favor, faça o upload do arquivo Excel para começar.")
