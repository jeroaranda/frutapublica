import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.title('La fruta esta aquí:')

def get_flora_data():
    return pd.read_csv('flora.csv')

df = get_flora_data()

#px.set_mapbox_access_token(open(".mapbox_token").read())
df['size'] = .5
fig = px.scatter_mapbox(df, lat="lat", lon="lon",  size='size',   color="flora inferida",mapbox_style="carto-positron",zoom=.7,
        hover_data=["id",
        "flora inferida",  # Display "Flora" instead of the full column name
        "usuario",
        "observaciones"]
    )
fig.update_traces(cluster=dict(enabled=True))
fig.show()
st.plotly_chart(fig, use_container_width=True) 
import os
images = [file for file in os.listdir() if file.endswith('.jpg')]
img = st.selectbox('Selecciona la imagen de flora:', images,0)
with open(img, "rb") as file:
    st.image(img, caption='Fruta seleccionada')
    btn = st.download_button(
            label="Descarga imagenes",
            data=file,
            file_name=img,
            mime="image/jpg"
        )
