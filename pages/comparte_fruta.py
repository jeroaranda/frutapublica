import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime, timedelta
import uuid
import pandas as pd

now = datetime.now()

st.title(f'Comparte fruta')

def get_flora_data():
    return pd.read_csv('flora.csv')
# Layout for the form

"### Formulario para capturar flora"

timeout = now + timedelta(hours = -6)
st.warning(f'Fecha  y hora: {timeout}')
df = get_flora_data()
options = list(df['flora inferida'].unique()) + ["Otra opción..."]
flora = st.selectbox("Flora:", options=options)
if flora == "Otra opción...":
    otroproducto = st.text_input("Añade tu opción de flora...",key='otroproducto')
    flora = otroproducto

options = list(df.usuario.unique()) + ["Otro usuario..."]
usuario = st.selectbox("Usuario", options=options)

if usuario == "Otro usuario...":
    otrousuario = st.text_input("Añade tu usuario...",key = 'otrousuario')
    usuario = otrousuario

location = streamlit_geolocation()
if location['latitude'] != None:
    st.write(f'Tu ubicación es: (lat:{location["latitude"]},lon:{location["longitude"]})')
    lat = location["latitude"]
    lon = location["longitude"]
else:
    otralocation = st.text_input("Añade la ubicación(latitud y longitud separadas por una coma)",key = 'otralocation')
    location = otralocation
    lat = None
    lon = None


img_file_buffer = st.camera_input("Toma una foto")




#fecha
observaciones = st.text_input('Observaciones')


if st.button("Capturar flora", type="primary"):
    id = uuid.uuid1()
    row = {"id":[id], "datetime":[timeout], "flora inferida":[flora], "usuario":[usuario],'lat':[lat],'lon':[lon],'dirección':[location],'observaciones':[observaciones]}
    df = pd.DataFrame(row)
    st.warning(f'Capturando{row}')
    if img_file_buffer is not None:
        # To read image file buffer as bytes:
        with open (f'{str(id)}.jpg','wb') as file:
            file.write(img_file_buffer.getbuffer())
        bytes_data = img_file_buffer.getvalue()
        
    df.to_csv('flora.csv',mode='a',index=False,header=False)
    st.rerun()






    
    


    


