import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar título da página
st.set_page_config(page_title='Análise de Horas Extras Realizadas', layout='wide')

# Função para formatar números no padrão brasileiro, incluindo anos
def format_number_brazilian(value):
    if isinstance(value, int):
        return f"{value}"
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Título da página
st.title('Análise de Horas Extras Realizadas')

# Sidebar para navegação
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Escolha a visualização:", ["Análise Geral", "Análise por Secretaria", "Análise por Cargo"])

# Solicitar o upload do arquivo Excel
uploaded_file = st.sidebar.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Função para carregar os dados com cache
    @st.cache_data(ttl=60)
    def load_data(file):
        # Carregar os dados da planilha
        data = pd.read_excel(file, sheet_name='base', usecols=['Ano', 'Mes', 'Matricula', 'Secretaria', 'Cod_Cargo', 'Cargo', 'Horas_realizadas'])
        # Converter a coluna 'Horas_realizadas' para numérico
        data['Horas_realizadas'] = pd.to_numeric(data['Horas_realizadas'], errors='coerce')
        # Garantir que a coluna 'Ano' seja tratada como inteiro
        data['Ano'] = data['Ano'].astype(int)
        return data

    # Carregar os dados uma única vez e armazenar em cache
    base_df = load_data(uploaded_file)

    # Criar um dicionário para mapear os meses para nomes curtos
    meses_dict = {
        1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
        7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez"
    }

    # Substituir os números dos meses pelos nomes correspondentes
    base_df['Mes'] = base_df['Mes'].map(meses_dict)

    # Se for Análise Geral ou Análise por Secretaria, adicionar seleção de Ano Inicial e Final
    if pagina in ["Análise Geral", "Análise por Secretaria"]:
        col1, col2 = st.columns(2)
        with col1:
            ano_inicial = st.selectbox('Selecione o Ano Inicial', sorted(base_df['Ano'].unique()))
        with col2:
            ano_final = st.selectbox('Selecione o Ano Final', sorted(base_df['Ano'].unique(), reverse=True))

        # Filtrar os dados pelo intervalo de anos selecionado
        filtered_data_by_year = base_df[(base_df['Ano'] >= ano_inicial) & (base_df['Ano'] <= ano_final)]
    else:
        filtered_data_by_year = base_df

    if pagina == "Análise por Secretaria":
        # Filtros Interativos na Visão Geral
        selected_secretaria = st.multiselect('Selecione a Secretaria', filtered_data_by_year['Secretaria'].unique())

        # Verificação se o usuário selecionou ao menos uma secretaria
        if not selected_secretaria:
            st.warning('Por favor, selecione ao menos uma secretaria para visualizar os dados.')
        else:
            # Filtragem dos Dados
            filtered_data = filtered_data_by_year[filtered_data_by_year['Secretaria'].isin(selected_secretaria)]

            # Agrupando por Cargo, Cod_Cargo e somando as horas realizadas
            detalhamento_data = filtered_data.groupby(['Cargo', 'Cod_Cargo', 'Ano']).agg({'Horas_realizadas': 'sum'}).reset_index()

            # Criar uma tabela pivô para exibir os dados com colunas para cada ano
            detalhamento_pivot = detalhamento_data.pivot_table(values='Horas_realizadas', index=['Cargo', 'Cod_Cargo'], columns='Ano', aggfunc='sum').fillna(0)
            
            # Aplicar a formatação numérica brasileira
            detalhamento_pivot_display = detalhamento_pivot.applymap(format_number_brazilian)

            # Gráfico de barras usando Plotly (mantendo o gráfico para os 10 principais cargos)
            top_10_grouped_data = detalhamento_data.groupby(['Cargo', 'Cod_Cargo']).agg({'Horas_realizadas': 'sum'}).reset_index()
            top_10_grouped_data = top_10_grouped_data.sort_values(by='Horas_realizadas', ascending=False).head(10)

            titulo_grafico = f'Horas Extras realizadas nas secretarias selecionadas entre {ano_inicial} e {ano_final}'
            st.subheader(titulo_grafico)

            fig_barras = px.bar(top_10_grouped_data, x='Cargo', y='Horas_realizadas', 
                            labels={'Horas_realizadas': 'Horas Extras'}, 
                            title=titulo_grafico)
            st.plotly_chart(fig_barras)

            # Exibição da Tabela de Dados Detalhados com colunas de ano
            st.subheader('Detalhamento dos Dados')
            st.write(detalhamento_pivot_display)
            
    elif pagina == "Análise Geral":
        # Agrupamento geral por Secretarias
        df_secretarias = filtered_data_by_year.groupby(['Ano', 'Secretaria']).agg({
            'Horas_realizadas': 'sum'
        }).reset_index()

        # Agrupamento geral por Cargos
        df_top_cargos = filtered_data_by_year.groupby(['Ano', 'Cod_Cargo', 'Cargo']).agg({
            'Horas_realizadas': 'sum'
        }).reset_index()

        # Manter as tabelas completas
        df_secretarias_pivot = df_secretarias.pivot_table(values='Horas_realizadas', index='Secretaria', columns='Ano', aggfunc='sum').fillna(0)
        df_top_cargos_pivot = df_top_cargos.pivot_table(values='Horas_realizadas', index='Cargo', columns='Ano', aggfunc='sum').fillna(0)

        # Aplicar a formatação numérica brasileira nas tabelas
        df_secretarias_pivot_display = df_secretarias_pivot.applymap(format_number_brazilian)
        df_top_cargos_display = df_top_cargos_pivot.applymap(format_number_brazilian)

        # Mostrar apenas os 10 valores mais altos para os gráficos
        top_10_secretarias = df_secretarias.groupby('Secretaria')['Horas_realizadas'].sum().nlargest(10).reset_index()
        top_10_cargos = df_top_cargos.groupby('Cargo')['Horas_realizadas'].sum().nlargest(10).reset_index()

        # Exibir gráfico de pizza para distribuição percentual de horas por secretaria (top 10)
        st.subheader('Distribuição Percentual de Horas por Secretaria')
        fig_pizza_secretarias = px.pie(top_10_secretarias, names='Secretaria', values='Horas_realizadas',
                                       title='Distribuição Percentual de Horas por Secretaria')
        fig_pizza_secretarias.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_pizza_secretarias)

        # Exibir gráfico de pizza para distribuição percentual de horas por cargo (top 10)
        st.subheader('Distribuição Percentual de Horas por Cargo')
        fig_pizza_cargos = px.pie(top_10_cargos, names='Cargo', values='Horas_realizadas',
                                  title='Distribuição Percentual de Horas por Código de Cargo')
        fig_pizza_cargos.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        st.plotly_chart(fig_pizza_cargos)

        # Exibir tabela de secretarias
        st.subheader('Horas Realizadas por Secretaria')
        st.dataframe(df_secretarias_pivot_display)

        # Exibir tabela de cargos
        st.subheader('Horas Realizadas por Cargo')
        st.dataframe(df_top_cargos_display)

    elif pagina == "Análise por Cargo":
        # Selecionar um cargo específico
        selected_cargo = st.selectbox('Selecione o Cargo', sorted(base_df['Cargo'].unique()))

        # Filtrar dados pelo cargo selecionado
        cargo_data = base_df[base_df['Cargo'] == selected_cargo]

        # Agrupar por ano e mês e somar as horas realizadas
        extrato_mensal = cargo_data.groupby(['Ano', 'Mes'])['Horas_realizadas'].sum().reset_index()

        # Ordenar os meses cronologicamente
        extrato_mensal['Mes'] = pd.Categorical(extrato_mensal['Mes'], categories=meses_dict.values(), ordered=True)
        extrato_mensal = extrato_mensal.sort_values(['Ano', 'Mes'])

        # Aplicar a formatação numérica brasileira
        extrato_mensal['Horas_realizadas'] = extrato_mensal['Horas_realizadas'].apply(format_number_brazilian)

        # Exibir os dados
        st.subheader(f'Extrato de Horas Realizadas - {selected_cargo}')
        st.dataframe(extrato_mensal)

        # Gráfico de barras das horas realizadas por mês
        fig_extrato = px.bar(extrato_mensal, x='Mes', y='Horas_realizadas', color='Ano',
                             labels={'Horas_realizadas': 'Horas Extras'}, 
                             title=f'Horas Extras Realizadas por Mês - {selected_cargo}')
        st.plotly_chart(fig_extrato)
else:
    st.info("Por favor, faça o upload do arquivo Excel para começar.")
