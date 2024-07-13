import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='centered'
)

st.write( '# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para o acompanhamento das métricas e crescimento dos Entregadores, Pedidos e Restaurantes.
    ### Como Utilizar este Growth Dashboard?
    - Visão Emrpesa:
        - Visão Gerencial: Métricas gerais e comportamentos
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Fernando Silva
        - e-mail: fernando.h.o.s@hotmail.com
'''
)   

#image_path = 'C:/Users/Fernando/OneDrive/TRAB/repos/'
image = Image.open ('target.png')
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company ' ) #markdown altera o nível e tamanho da fonte que está no parênteses dependendo de quantos '#' existirem
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( '''---''' )
