import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from Home import get_fruit

st.title('La fruta esta aquí:')

df = get_fruit()
df['lat'] = df.location.apply(lambda x: float(x.split(',')[0]))
df['lon'] = df.location.apply(lambda x: float(x.split(',')[1]))
st.dataframe(df[['lat','lon','inferred_fruit']])

#px.set_mapbox_access_token(open(".mapbox_token").read())
df['size'] = .7
fig = px.scatter_mapbox(df, lat="lat", lon="lon",  size='size',   color="inferred_fruit",mapbox_style="carto-positron",zoom=.7)
fig.update_traces(cluster=dict(enabled=True))
fig.show()
st.plotly_chart(fig)