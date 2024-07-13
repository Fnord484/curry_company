import pandas as pd
import streamlit as st
from haversine import haversine
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

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


def top_delivers( df, top_asc ):
    df_aux = (df.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
            .groupby(['City','Delivery_person_ID'])
            .mean()
            .sort_values(['City','Time_taken(min)'], ascending= top_asc)
            .reset_index()
            )

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10)

    df_aux = pd.concat([ df_aux1 , df_aux2 , df_aux3 ]).reset_index(drop=True)
    return df_aux
            

#============================================= Início da Estrutura Lógica do Código =============================================

#=============================================
# Importando a base
#=============================================
df = pd.read_csv("C:/Users/Fernando/OneDrive/TRAB/repos/data_sets/comunidade_ds/train.csv")

#Create Backup
df_backup = df.copy()

df = clean_code( df )

#Create Filter Bakup
df_filtered = df.copy()

#=============================================
# Barra Lateral
#=============================================
#colocando o título na página
st.header('Marketplace - Visão Entregadores')

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

tab1, tb2, tb3 = st.tabs( [ 'Visão Gerencial', '_', '_' ])

with tab1:
    with st.container():
            col1, col2, col3, col4 = st.columns( 4, gap='large')
            with col1:
                #Caixa com valor da maior idade
                maior_idade = df['Delivery_person_Age'].max()
                col1.metric('Maior Idade',maior_idade)

            with col2:
                #Caixa com valor da menor idade
                menor_idade = df['Delivery_person_Age'].min()
                col2.metric('Menor Idade',menor_idade)

            with col3:
                #Caixa com valor da melhor condição de veículo
                melhor_condição =df['Vehicle_condition'].max()
                col3.metric('Melhor condição de Veículo',melhor_condição)

            with col4:
                #Caixa com valor da pior condição de veículo
                pior_condição= df['Vehicle_condition'].min()
                col4.metric('Pior condição de Veículo',pior_condição)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('#### Avaliações médias por entregador')
            df_avg_ratings_per_deliver = (df.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                      .groupby('Delivery_person_ID')
                      .mean()
                      .round(2)
                      .reset_index())
            df_avg_ratings_per_deliver.columns = [ 'Delivery_person_ID' , 'Avg_Person_Ratings' ]
            st.dataframe(df_avg_ratings_per_deliver)
        
        with col2:
            st.markdown( '##### Avaliação média por Trânsito' )
            df_rating_by_traffic = (df.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                    .groupby(['Road_traffic_density'])
                                    .agg({'Delivery_person_Ratings': ['mean', 'std']})
                                    .reset_index()
                                    )
            #Renomeando as colunas
            df_rating_by_traffic.columns = ['Road_traffic_density','Rating_mean','Rating_std']
            df_rating_by_traffic.reset_index()
            st.dataframe(df_rating_by_traffic)

            st.markdown('##### Avaliação média por Clima')
            df_rating_by_weatherconditions =(df.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                             .groupby('Weatherconditions')
                                             .agg({'Delivery_person_Ratings': ['mean','std']})
                                             .reset_index()
                                            )       
            df_rating_by_weatherconditions.columns = ['Weatherconditions', 'Rating_mean', 'Rating_std']
            st.dataframe(df_rating_by_weatherconditions)
    
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df_aux = top_delivers( df, top_asc=True )
            st.dataframe(df_aux)
            
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
           
            df_aux = top_delivers( df, top_asc=False )
            st.dataframe(df_aux)
              

             