import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar título da página
st.set_page_config(page_title='Análise de Horas Extras Realizadas', layout='wide')

# Função para formatar números no padrão brasileiro, incluindo anos
def format_number_brazilian(value):
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
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

    if pagina == "Análise por Secretaria":
        # Filtros Interativos na Visão Geral
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

            # Nome do gráfico dinâmico (subheader)
            titulo_grafico = f'Horas Extras realizadas na {", ".join(map(str, selected_secretaria))} em {", ".join(map(str, selected_years))}'
            st.subheader(titulo_grafico)

            # Gráfico de barras usando Plotly
            fig_barras = px.bar(top_10_grouped_data, x='Cargo', y='Horas_realizadas', 
                                labels={'Horas_realizadas': 'Horas Extras'}, 
                                title=titulo_grafico)
            st.plotly_chart(fig_barras)

            # Aplicando a formatação numérica brasileira
            grouped_data['Horas_realizadas'] = grouped_data['Horas_realizadas'].apply(format_number_brazilian)

            # Exibição da Tabela de Dados Detalhados
            st.subheader('Detalhamento dos Dados')
            st.write(grouped_data)

    elif pagina == "Análise Geral":
        # Agrupamento geral por Secretarias e Cargos
        df_secretarias = base_df.groupby('Secretaria').agg({
            'Horas_realizadas': 'sum'
        }).sort_values(by='Horas_realizadas', ascending=False).head(10).reset_index()

        df_top_cargos = base_df.groupby(['Cod_Cargo', 'Cargo']).agg({
            'Horas_realizadas': 'sum'
        }).sort_values(by='Horas_realizadas', ascending=False).head(10).reset_index()

        # Aplicando a formatação numérica brasileira nas tabelas
        df_secretarias_display = df_secretarias.copy()
        df_top_cargos_display = df_top_cargos.copy()

        df_secretarias_display['Horas_realizadas'] = df_secretarias_display['Horas_realizadas'].apply(format_number_brazilian)
        df_top_cargos_display['Horas_realizadas'] = df_top_cargos_display['Horas_realizadas'].apply(format_number_brazilian)

        # Colocar Tabela 1 e Gráfico 1 lado a lado
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('Secretarias com mais Horas Realizadas')
                st.dataframe(df_secretarias_display)
            
            with col2:
                st.subheader('Distribuição Percentual de Horas por Secretaria')
                fig_pizza_secretarias = px.pie(df_secretarias, names='Secretaria', values='Horas_realizadas',
                                               title='Distribuição Percentual de Horas por Secretaria')
                fig_pizza_secretarias.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                st.plotly_chart(fig_pizza_secretarias)

        # Colocar Tabela 2 e Gráfico 2 lado a lado
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('Cargos com mais Horas Realizadas')
                st.dataframe(df_top_cargos_display)
            
            with col2:
                st.subheader('Distribuição Percentual de Horas por Cargo')
                fig_pizza_cargos = px.pie(df_top_cargos, names='Cod_Cargo', values='Horas_realizadas',
                                          title='Distribuição Percentual de Horas por Código de Cargo')
                fig_pizza_cargos.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
                st.plotly_chart(fig_pizza_cargos)

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
        extrato_mensal['Ano'] = extrato_mensal['Ano'].apply(format_number_brazilian)

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
