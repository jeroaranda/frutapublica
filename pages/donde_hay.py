import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from Home import get_or_create_flora_data

st.title('La fruta esta aquí:')

df = get_or_create_flora_data()
st.dataframe(df[['lat','lon','flora inferida']])

#px.set_mapbox_access_token(open(".mapbox_token").read())
df['size'] = .7
fig = px.scatter_mapbox(df, lat="lat", lon="lon",  size='size',   color="flora inferida",mapbox_style="carto-positron",zoom=.7,
        hover_data={
        "Flora": "flora inferida",  # Display "Flora" instead of the full column name
        "Usuario": "usuario",
        "Observations": "observaciones"
    })
fig.update_traces(cluster=dict(enabled=True))
fig.show()
st.plotly_chart(fig, use_container_width=True) 