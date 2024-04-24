import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime

now = datetime.now()

st.title(f'Comparte fruta {now}')

# Layout for the form

"### Formulario para capturar flora aprovechable"

options = ['limón','mango','mandarina','gasparito'] + ["Otra opción..."]
producto = st.selectbox("Selecciona una opción", options=options)

if producto == "Otra opción...":
    otroproducto = st.text_input("Añade tu opción...",key='otroproducto')

options = ['jero','nacho'] + ["Otra opción..."]
usuario = st.selectbox("Selecciona una opción", options=options)

if usuario == "Otra opción...":
    otrousuario = st.text_input("Añade tu opción...",key = 'otrousuario')

location = streamlit_geolocation()
if location['latitude'] != None:
    st.write(f'Your location is (lat:{location["latitude"]},lon:{location["longitude"]})')
img_file_buffer = st.camera_input("Toma una foto")

if img_file_buffer is not None:
    # To read image file buffer as bytes:
    bytes_data = img_file_buffer.getvalue()
    # Check the type of bytes_data:
    # Should output: <class 'bytes'>
    st.write(type(bytes_data))
#fecha
observaciones = st.text_input('Observaciones')

if st.button("Capturar flora", type="primary"):
    st.write('Capturando')


    
    


    


