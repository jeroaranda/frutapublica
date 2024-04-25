import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import imageio
import requests
import time
import plotly.express as px
import pandas as pd
import os
import base64


@st.cache_data
def get_fruit():
  url = 'https://github.com/ecastillomon/fruta-publica/blob/main/cache/temp.csv'
  df = pd.read_csv('data/temp.csv')
  #df2 = pd.read_csv(url)
  return df
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')
@st.cache_data
def get_or_create_flora_data():
    """
    Checks if a CSV file named "flora.csv" exists.
    - If it exists, reads the data into a pandas DataFrame.
    - If it doesn't exist, creates a new DataFrame with specific columns
      and saves it as "flora.csv".

    Returns:
        pandas.DataFrame: The loaded or created DataFrame containing flora data.
    """

    # Define the file path
    file_path = "flora.csv"

    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing data
        try:
            data = pd.read_csv(file_path)
            return data
        except pd.errors.EmptyDataError:
            # Handle empty CSV gracefully (potentially create a new one)
            print("Existing 'flora.csv' is empty. Creating a new one with default columns.")
            return create_and_save_flora_data(file_path)

    else:
        # Create the DataFrame with specified columns
        return create_and_save_flora_data(file_path)

def create_and_save_flora_data(file_path):
    """
    Creates a new pandas DataFrame with specific columns ("species", "location", etc.)
    and saves it to the provided file path.

    Args:
        file_path (str): The path to save the newly created CSV file.

    Returns:
        pandas.DataFrame: The newly created DataFrame containing flora data.
    """

    # Define the desired columns (replace with your actual column names)
    columns = ["id", "datetime", "flora inferida", "usuario",'lat','lon','dirección','observaciones']
    
    df = get_fruit()
    df = df.reset_index()
    df['lat'] = df.location.apply(lambda x: float(x.split(',')[0]))
    df['lon'] = df.location.apply(lambda x: float(x.split(',')[1]))
    df.rename(columns={'index':'id','date':'datetime','user':'usuario','text':'observaciones','location':'dirección','inferred_fruit':'flora inferida'},inplace=True)

    # Create a new empty DataFrame
    data = pd.DataFrame(columns=columns)
    data = pd.concat([data,df[columns]])
    # Save the DataFrame to CSV (optional, depending on your app's logic)
    data.to_csv(file_path, index=False)

    return data
   
def main():
    # Set the title and description of the app
    st.set_page_config(layout="wide")
    st.title("La Fruta Pública")
    df = get_or_create_flora_data()

    #plot fruits by people
    #df.groupby('inferred_fruit')['index'].count().plot()

    df = df.fillna('Desconocido')
    col1, col2, col3 = st.columns(3)
    col1.metric("Flora totales:", df.shape[0])
    col2.metric("Diversidad floral:", df['flora inferida'].nunique())
    col3.metric("Usuarios registradas:", df.usuario.nunique())
    # Create the bar plot using Plotly
    data_grouped = df.groupby(['flora inferida', 'usuario'])['id'].count().reset_index()
    
    #fig.update_layout(title='Flora Inferences by User', xaxis_title='Flora Inferred', yaxis_title='Count')



    # Sort the carriers by the total number of tracking numbers
    # "order = group_df.groupby(['carrier'])['tracking_number'].sum().sort_values().index.to_list()

    # Create the chart
    fig = px.bar(data_grouped, x='flora inferida', y='id', color='usuario', title='Número de envíos por carrier y app', barmode='stack', )#category_orders={'carrier': order[::-1]})

    # Set the axis labels
    fig.update_xaxes(title='Frutas')
    fig.update_yaxes(title='Mapeadas')

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    "### Descarga"
    "Ejemplo de data:"
    st.dataframe(df.head())

    csv = convert_df(df)
    st.download_button(
    "Descargar",
    csv,
    "flora.csv",
    "text/csv",
    key='download-csv'
    )
    images = [file for file in os.listdir() if file.endswith('.jpg')]
    img = st.sidebar.multiselect('Selected img', images,images[0])
    with open(img, "rb") as file:
        btn = st.download_button(
                label="Download image",
                data=file,
                file_name=img,
                mime="image/jpg"
            )



if __name__ == '__main__':
    main()
