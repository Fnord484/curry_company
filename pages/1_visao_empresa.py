import pandas as pd
import streamlit as st
from haversine import haversine
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium

from streamlit_folium import folium_static

st.set_page_config( page_title= 'Visão Empresa', page_icon='📈', layout='wide')

#=============================================
# Funções
#=============================================

#Função de limpeza
def clean_code( df ):
    '''Esta função tem a útilidade de limpar o Data Frame
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espácos dos valores tipo object
        4. Formatação da coluna de datas
        5. Limpeza do texto do valores da coluna de tempo
    
        Input: Dataframe
        Output: Dataframe
    '''



    #1. convertendo a coluna Age de texto para inteiro
    linhas_sem_vazio = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_sem_vazio,:].copy()

    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    linhas_sem_vazio = (df['Delivery_person_Ratings'] != 'NaN ')

    #2. convertendo a coluna Ratings de texto para float
    df = df.loc[linhas_sem_vazio,:].copy()

    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # 3. convertendo a coluna Order_Date de texto para data

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format = '%d-%m-%Y')


    # 4. convertendo multiploe_deliverys de texto para int
    linhas_sem_vazio = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_sem_vazio,:]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

        #ou
    # df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')
    # df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')
    # df['multiple_deliveries'] = pd.to_numeric(df['multiple_deliveries'], errors='coerce')

    #5. removendo os espaços dentro de strings/objects
    def remover_espacos (texto):
            return texto.str.replace(' ', '')

    colunas_processar = ['ID', 'Delivery_person_ID','Festival', 'City', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle']
    df[colunas_processar] = df[colunas_processar].apply(remover_espacos)
        
        #ou

    # for i in range( len( df ) ): 
    # 	df.loc[i, 'ID'] = df.loc[i, 'ID'].strip() 
    # 	df.loc[i, 'Delivery_person_ID'] = df.loc[i, 'Delivery_person_ID'].strip()
        
        #ou
    #df.loc[:,'ID'] = df.loc[:, 'ID'].str.strip()
            
    linhas_sem_vazio = df['City'] != 'NaN'
    df = df.loc[linhas_sem_vazio,:]
    df.reset_index()

    linhas_sem_vazio = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_sem_vazio, :]

    linhas_sem_vazio = df['Festival'] != 'NaN'
    df = df.loc[linhas_sem_vazio,:]
    df['Week_of_Year'] = df['Order_Date'].dt.strftime('%U')

    #Resetando os índices
    df = df.reset_index( drop = True )

    return df

def order_metric(df):
                #agrupamento da pedidos por dia
                df_aux = df.loc[:,['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
                fig = px.bar(df_aux,x='Order_Date',y='ID')
                return fig    

def traffic_order_share(df):
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    fig = px.pie(df_aux,names= 'Road_traffic_density',values='ID',template= 'plotly_dark')
    return fig

def traffic_order_city(df):
    df_aux = df.loc[:,['ID', 'Road_traffic_density','City']].groupby(['Road_traffic_density','City']).count().reset_index()
    df_aux['%Entregas'] = 100* (df_aux['ID'] / df_aux['ID'].sum())
    fig = px.scatter(df_aux,x='City', y='Road_traffic_density',size='%Entregas')
    return fig

def order_by_week(df):
    df_aux = df.loc[:, ['ID','Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
    fig = px.line( df_aux, x='Week_of_Year', y='ID')
    return fig

def order_by_delivers( df ):
    df_aux = df.loc[:,['ID','Delivery_person_ID','Week_of_Year']].groupby('Week_of_Year').nunique().reset_index()
    df_aux['order_by_delivers'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux,x='Week_of_Year',y='order_by_delivers',template= 'plotly_dark')
    return fig

def country_map( df ):
    df_aux = (df.loc[:,['City','Delivery_location_longitude','Delivery_location_latitude','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index()
                )
    map_ = folium.Map()
    for index,location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup= location_info[['City','Road_traffic_density']]).add_to( map_ )
    folium_static( map_, width=900, height=600)
    return None
#============================================= Início da Estrutura Lógica do Código =============================================

#=============================================
# Importando a base
#=============================================

df = pd.read_csv("data_sets/comunidade_ds/train.csv")

#Create Backup
df_backup = df.copy()

df = clean_code( df )

#Create Filter Bakup
df_filtered = df.copy()

#=============================================
# Barra Lateral
#=============================================
#colocando o título na página
st.header('Marketplace - Visão Empresa')

#Inserindo uma imagem na sidebar
image_path = 'target.png'
image= Image.open( image_path ) #lendo a imagem da mesma pasta com a biblioteca Image
st.sidebar.image( image, width=120) #Inserindo a imagem na sidebar

#colocando uma barra lateral com o texto cury company
st.sidebar.markdown( '# Cury Company ' ) #markdown altera o nível e tamanho da fonte que está no parênteses dependendo de quantos '#' existirem
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( '''---''' )

#Filtro de data
date_slider = st.sidebar.slider(
        'Selecione uma data:',
        value=datetime( 2022, 4, 6 ),
        min_value=datetime( 2022, 2, 11 ),
        max_value=datetime( 2022, 4, 6 ),
        format='DD/MM/YYYY')

st.sidebar.markdown( '''---''' )

#Filtro de densidade de trafego
traffic_options = st.sidebar.multiselect( 
        'Quais as condições do trânsito',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''----''')
st.sidebar.markdown( '### Powered by Stramlit')

linhas_selecionadas = df['Order_Date'] <= date_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options ) #isin = 'está em' 
df = df.loc[linhas_selecionadas, : ]

#=============================================
# Layout no Streamlit
#=============================================

tab1, tab2, tab3 = st.tabs([ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: #tudo que tiver identado dentro do with tab1 vale para o tab1
        #Englobando containers que são as áreas para colocar, neste caso, os gráficos
        with st.container():
            st.markdown('# Pedidos por dia')
            fig = order_metric( df )
            st.plotly_chart(fig, use_container_width=True) #o st.plotly_char carrega gráficos ou objetos do plotly, e o use_container_widith faz o gráfico não ultrapassar o tamanho da página

        #criando um segundo container na tab para colocar o gráfico nele.
        #Este conteiner tem duas colunas com gráficos
        with st.container():
            col1, col2 = st.columns( 2 )#criando as duas colunas
            
            with col1: #O que contem na primeira coluna
                st.markdown( '## Pedidos por tipo de trafego' )
                fig = traffic_order_share( df )
                st.plotly_chart(fig, use_container_width= True)
        
            with col2: #o que contem na segunda coluna
                st.markdown( '## Pedidos por cidade' )
                fig = traffic_order_city( df )
                st.plotly_chart(fig, use_container_width=True)

with tab2:
        with st.container():
            st.markdown('# Pedidos por Semana')
            fig = order_by_week( df )
            st.plotly_chart(fig, use_container_width=True)
        
        with st.container():
            st.markdown('# Pedidos por Entregadores Únicos')
            fig = order_by_delivers( df )
            st.plotly_chart(fig, use_container_width=True)
              

with tab3: #Visão Geográfica
        st.markdown('# Country Map')
        country_map( df )

