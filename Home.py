import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import imageio
import requests
import time
import plotly.graph_objects as go
import pandas as pd


@st.cache_data
def get_fruit():
  url = 'https://github.com/ecastillomon/fruta-publica/blob/main/cache/temp.csv'
  df = pd.read_csv('data/temp.csv')
  #df2 = pd.read_csv(url)
  return df
def main():
    # Set the title and description of the app
    st.set_page_config(layout="wide")
    st.title("La Fruta Pública")
    df = get_fruit()
    df = df.reset_index()
    st.dataframe(df)
    df = df.fillna('Desconocido')
    col1, col2, col3 = st.columns(3)
    col1.metric("Frutas registradas:", df.shape[0])
    st.dataframe(df.groupby(['user','inferred_fruit'])['index'].count())
    


        

if __name__ == '__main__':
    main()
