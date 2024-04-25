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
import pandas as pd
import os

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
    df.rename(columns={'index':'id','date':'datetime','user':'usuario','text':'observaciones','direccion':'location','inferred_fruit':'flora inferida'})

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
    df = df.reset_index()
    #plot fruits by people
    #df.groupby('inferred_fruit')['index'].count().plot()
    st.dataframe(df)
    df = df.fillna('Desconocido')
    col1, col2, col3 = st.columns(3)
    col1.metric("Frutas registradas:", df.shape[0])
    st.dataframe(df.groupby(['flora inferida','user'])['index'].count())
    
    # Create the bar plot using Plotly
    data_grouped = df.groupby(['flora inferida', 'user'])['index'].count().reset_index()
    fig = go.Figure(data=[go.Bar(x=data_grouped['flora inferida'], y=data_grouped['index'], color=data_grouped['user'])])
    fig.update_layout(title='Flora Inferences by User', xaxis_title='Flora Inferred', yaxis_title='Count')

    # Use the loaded or created flora_data and the figure (`fig`) in your Streamlit app logic

    st.plotly_chart(fig)  # Display the Plotly bar chart


        

if __name__ == '__main__':
    main()
