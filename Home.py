import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import plotly.express as px
import uuid
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
from database.database_utils import (
    get_observations_df, 
    add_observation, 
    get_recipes, 
    add_recipe,
    get_db_session
)
from models import Flora, User

def main():
    st.set_page_config(layout="wide")
    st.title("La Fruta Pública")
    
    # Navigation
    page = st.sidebar.radio("Páginas", ["Mapa", "Comparte flora", "Recetas", "Analytics"])
    
    if page == "Mapa":
        show_map_view()
    elif page == "Comparte flora":
        share_flora()
    elif page == "Recetas":
        show_recipes()
    elif page == "Analytics":
        show_analytics()

from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

import io
import os.path
import pickle

def setup_google_drive():
    """Sets up Google Drive authentication using Streamlit secrets."""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["google_credentials"],
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        raise Exception(f"Error setting up Google Drive: {str(e)}")
    


def upload_to_drive(img_file_buffer, description, folder_id=None,observation_id=None):
    """
    Uploads an image to Google Drive
    
    Parameters:
    img_file_buffer: StreamlitUploadedFile - The image buffer from st.camera_input
    description: str - Description/observations for the image
    folder_id: str - Optional Google Drive folder ID to upload to
    
    Returns:
    str: The file ID of the uploaded image
    """
    try:
        # Initialize Google Drive service
        service = setup_google_drive()
        
        # Prepare the file metadata
        file_metadata = {
            'name': f'observation_{str(observation_id)}.jpg',
            'description': description
        }
        
        # If folder_id is provided, add it to metadata
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Create media upload object
        media = MediaIoBaseUpload(
            io.BytesIO(img_file_buffer.getvalue()),
            mimetype='image/jpeg',
            resumable=True
        )
        
        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
        
    except Exception as e:
        raise Exception(f"Error uploading to Google Drive: {str(e)}")
def show_map_view():
    st.header("Mapa de Flora")
    
    

    df = get_observations_df()
    df['shortdescription'] = df['description'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
    df['size'] = 10
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    # Get unique fruits
    fruits = df['flora_name'].unique()

    # Create color mapping using Plotly's qualitative colors
    color_palette = px.colors.qualitative.D3
    colors = [color_palette[i % len(color_palette)] for i in range(len(fruits))]
    color_map = dict(zip(fruits, colors))

    # Add color column
    df['color'] = df['flora_name'].map(color_map)

    # Create the map
    # st.map(
    #     data=df,
    #     latitude='lat',
    #     longitude='lon',
    #     size='size',
    #     color='color'
    # )

    # # Your original map code
    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        size='size',
        color="flora_name",
        zoom=2.9,
        size_max=10,
        hover_data=["id", "flora_name", "username", "shortdescription"],map_style="basic"
    )

    fig.update_traces(cluster=dict(enabled=False))

    st.plotly_chart(fig, use_container_width=True)
    
    # Add download button
    st.download_button(
        label="Descargar datos (CSV)",
        data=df[['datetime','address','lat','lon','description','id','flora_name','username']].to_csv(index=False).encode('utf-8'),
        file_name='flora_data.csv',
        mime='text/csv'
    )

def share_flora():
    st.header("Comparte flora")
    
    session = get_db_session()
    flora_options = [f.name for f in session.query(Flora).all()] + ["Otro..."]
    user_options = [u.username for u in session.query(User).all()] + ["Otro..."]
    session.close()
    
    # Form inputs
    flora = st.selectbox("Flora:", options=flora_options)
    if flora == "Otro...":
        flora = st.text_input("Añade tu opción de flora...")
    
    username = st.selectbox("Usuario:", options=user_options)
    if username == "Otro...":
        username = st.text_input("Añade un nuevo usuario...")
    
    # Get location
    location = streamlit_geolocation()
    if location['latitude'] is not None:
        lat = location["latitude"]
        lon = location["longitude"]
        st.write(f"Tu ubicación: ({lat}, {lon})")
    else:
        location_input = st.text_input("Añade tu ubicación (latitud,longitud) o dirección:")
        try:
            lat, lon = map(float, location_input.split(','))
        except:
            lat = lon = None
    
    address = st.text_input("Dirección (opcional):")

    img_file_buffer = st.camera_input("Toma una foto")
    UPLOAD_URL = "https://drive.google.com/drive/folders/1yj0_LawzPpLXMYbF15xyfFgoxsB69M8t"
    description = st.text_area("Observaciones:")
    
    if st.button("Submit", type="primary"):
        if all([flora, username, lat, lon]):
            observation_id = add_observation(flora, username, lat, lon, address, description)
            st.success("Observación grabada correctamente!")
            if img_file_buffer is not None:
                try:
                    # Replace with your Google Drive folder ID
                    FOLDER_ID = "1yj0_LawzPpLXMYbF15xyfFgoxsB69M8t"  
                    
                    file_id = upload_to_drive(
                        img_file_buffer,
                        description,
                        folder_id=FOLDER_ID,
                        observation_id=observation_id
                    )
                    
                    st.success("¡Observación y foto grabadas correctamente!")
                    st.write(f"File ID in Google Drive: {file_id}")
                except Exception as e:
                    st.error(f"Error uploading to Google Drive: {str(e)}")

        else:
            st.error("Por favor, rellena todos los campos requeridos.")

def show_recipes():
    st.header("Recetas públicas")
    
    # Tab selection
    tab1, tab2 = st.tabs(["Explora recetas", "Añade receta"])
    
    with tab1:
        recipes = get_recipes()
        for recipe in recipes:
            with st.expander(recipe['name']):
                st.write("**Ingredientes:**")
                for ingredient in recipe['ingredients']:
                    st.write(f"- {ingredient}")
                st.write("\n**Preparación:**")
                st.write(recipe['prep'])
    
    with tab2:
        st.subheader("Añade nueva receta")
        
        name = st.text_input("Receta:")
        
        session = get_db_session()
        available_flora = [f.name for f in session.query(Flora).all()]
        session.close()
        
        ingredients = st.multiselect("Ingredientes:", available_flora)
        prep = st.text_area("Preparación:")
        
        if st.button("Añadir receta"):
            if name and ingredients and prep:
                add_recipe(name, prep, ingredients)
                st.success("Receta añadida correctamente!")
                st.rerun()
            else:
                st.error("Porfavor, rellena todos los campos.")

def show_analytics():
    st.header("Analytics")
    
    df = get_observations_df()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Flora totales:", df.flora_name.nunique())
        st.metric("Observaciones:", df.shape[0])
    with c2:
        st.metric("Observaciones por usuario:", df.shape[0]/df.username.nunique())
        st.metric("Usuarios registrados:", df.username.nunique())
        
    data_grouped = df.groupby(['flora_name', 'username'])['id'].count().reset_index()

     # Create the chart
    fig = px.bar(data_grouped, x='flora_name', y='id', color='username', title='Diversidad florar por usuario', barmode='stack', )#category_orders={'carrier': order[::-1]})

    # Set the axis labels
    fig.update_xaxes(title='Frutas')
    fig.update_yaxes(title='Mapeadas')

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        
        # Flora distribution
        fig1 = px.bar(
            df['flora_name'].value_counts().reset_index(),
            x='flora_name',
            y='count',
            title='Flora Distribution',
            labels={'index': 'Flora Type', 'flora_name': 'Count'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        
        # User activity
        fig2 = px.bar(
            df['username'].value_counts().reset_index(),
            x='username',
            y='count',
            title='User Activity',
            labels={'index': 'User', 'username': 'Observations'}
        )
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == '__main__':
    main()