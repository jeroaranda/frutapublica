import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime, timedelta
import uuid

now = datetime.now()

st.title(f'Comparte fruta')

# Layout for the form

"### Formulario para capturar flora aprovechable"
id = uuid.uuid4()
st.warning(str(id))
timeout = now + timedelta(hours = -6)
st.warning(f'Fecha  y hora: {timeout}')

options = ['limón','mango','mandarina','gasparito'] + ["Otra opción..."]
producto = st.selectbox("Flora:", options=options)

if producto == "Otra opción...":
    otroproducto = st.text_input("Añade tu opción de flora...",key='otroproducto')

options = ['jero','nacho'] + ["Otro usuario..."]
usuario = st.selectbox("Usuario", options=options)

if usuario == "Otro usuario...":
    otrousuario = st.text_input("Añade tu usuario...",key = 'otrousuario')

location = streamlit_geolocation()
if location['latitude'] != None:
    st.write(f'Your location is (lat:{location["latitude"]},lon:{location["longitude"]})')
img_file_buffer = st.camera_input("Toma una foto")

if img_file_buffer is not None:
    # To read image file buffer as bytes:
    bytes_data = img_file_buffer.getvalue()
    with open (f'data/imagenes/{str(id)}.jpg','wb') as file:
          file.write(img_file_buffer.getbuffer())
    
#fecha
observaciones = st.text_input('Observaciones')

if st.button("Capturar flora", type="primary"):
    st.write('Capturando')


    
    


    


