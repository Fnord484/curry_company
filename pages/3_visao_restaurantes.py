import pandas as pd
import streamlit as st
from haversine import haversine
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

import plotly.graph_objects as go

st.set_page_config( page_title= 'Visão Restaurantes', page_icon='🍽', layout='wide')

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

    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split( '(min) ' )[1] )
    df.reset_index()
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )

    #Resetando os índices
    df = df.reset_index( drop = True )

    return df

def calculate_distance(df):
    colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df['Distancia'] = df.loc[:, colunas].apply( lambda x: 
                        haversine( 
                            (x['Restaurant_latitude'] , x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1)
    
    avg_distance = df['Distancia'].mean().round(2)
    return avg_distance

def times_by_city( df ):
    df_aux =df.loc[:,['City', 'Time_taken(min)']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std'] }).reset_index()

    df_aux.columns = ['City', 'mean_Time_taken(min)', 'std_Time_taken(min)']


    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['mean_Time_taken(min)'],
                        error_y=dict(type='data', array = df_aux['std_Time_taken(min)'] ) ) )

    fig.update_layout(barmode='group')
    return fig

def calculte_times_festival( df, festival, operation ):
    df_aux = (df.loc[:,['Festival','Time_taken(min)']]
            .groupby( ['Festival'])
            .agg( {'Time_taken(min)':['mean','std']})
            #   .reset_index()
            )
    
    # df_aux.columns = ['Festival', 'mean_Time_taken(min)','std_Time_taken(min)']
    line = 0
    col = 0
    if festival == True:
        line = 1
    elif operation == 'std':
        col = 1
    time = df_aux.iloc[line,col].round(2)
    return time


def data_times_by_city_typeOrder( df ):
    df_aux = (df.loc[:,['City', 'Time_taken(min)','Type_of_order']]
        .groupby(['City', 'Type_of_order'])
        .agg({'Time_taken(min)': ['mean', 'std'] })
        .reset_index()
)

    df_aux.columns = ['City', 'Type_of_order', 'mean_Time_taken(min)', 'std_Time_taken(min)']
    return df_aux


def distance_by_city( df ):
    colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df['Distancia'] = df.loc[:, colunas].apply( lambda x: 
                        haversine( 
                            (x['Restaurant_latitude'] , x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1)

    avg_distance = (df.loc[:,['City', 'Distancia']]
                    .groupby( [ 'City' ] )
                    .mean()
                    .reset_index()
                    )


    fig = go.Figure( data=[go.Pie( labels = avg_distance['City'], values=avg_distance['Distancia'], pull=[0, 0.1, 0 ])]) 
    return fig

def time_by_city_traffic_density( df ):
                    df_aux = (df.loc[:,['Road_traffic_density', 'Time_taken(min)', 'City']]
                            .groupby(['City', 'Road_traffic_density'])
                            .agg({'Time_taken(min)': ['mean','std']})
                            .reset_index()
                            )

                    df_aux.columns = ['City', 'Road_traffic_density', 'mean_Time_taken(min)', 'std_Time_taken(min)']

                    fig = px.sunburst(df_aux,path=['City', 'Road_traffic_density'], values= 'mean_Time_taken(min)',
                                    color='std_Time_taken(min)', color_continuous_scale='RdBu',
                                    color_continuous_midpoint=np.average(df_aux['std_Time_taken(min)']))
                    return fig
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
st.header('Marketplace - Visão Restaurantes')

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
        'Selecione uma data',
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

tab1,tab2,tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        col1,col2,col3,col4,col5,col6 = st.columns( 6, gap='large' )

        with col1:
            entregadores_unicos = df['Delivery_person_ID'].nunique()
            col1.metric('Entregadores',entregadores_unicos )

        with col2:
            avg_distance = calculate_distance( df )
            col2.metric('Distância Média', avg_distance)

        with col3:
            avg_time_festival = calculte_times_festival( df, festival=True,operation='mean')
            col3.metric('Tempo Médio c/Festival', avg_time_festival)

        with col4:
            std_time_festival = calculte_times_festival( df, festival= True, operation='std')
            col4.metric('Desvio Padrão c/Festival', std_time_festival)

        with col5:
            avg_time_nofestival = calculte_times_festival( df, festival= False, operation='mean')
            col5.metric('Tempo Médio s/Festival', avg_time_nofestival)

        with col6:
            std_time_nofestival = calculte_times_festival( df, festival= False, operation='std')
            col6.metric('Desvio Padrão s/Festival', std_time_nofestival)

        st.markdown('''----''')

    with st.container():
        col1,col2 = st.columns(2, gap='large')
        
        with col1:

            fig = times_by_city( df )
            col1.plotly_chart(fig, use_container_width=True)

        with col2:
            df_aux = data_times_by_city_typeOrder( df )
            col2.dataframe(df_aux)

    with st.container():
        st.markdown('''----''')
        st.title('Distribuição de Tempo')
        col1,col2 = st.columns(2)

        with col1:
            fig = distance_by_city( df )
            col1.plotly_chart(fig, use_container_width= True)

        with col2:
            fig = time_by_city_traffic_density( df )
            
            col2.plotly_chart(fig, use_container_width=True)
        
