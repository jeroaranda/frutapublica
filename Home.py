import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import plotly.express as px
import uuid
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

def show_map_view():
    st.header("Mapa de Flora")
    
    df = get_observations_df()
    
    
    # Create map
    df['size'] = .2
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size='size',
        color="flora_name",
        mapbox_style="carto-positron",
        zoom=2.8,
        size_max=5,
        hover_data=["id", "flora_name", "username", "description"]
    )
    fig.update_traces(cluster=dict(enabled=True))
    st.plotly_chart(fig, use_container_width=True)

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

    description = st.text_area("Observaciones:")
    
    if st.button("Submit", type="primary"):
        if all([flora, username, lat, lon]):
            add_observation(flora, username, lat, lon, address, description)
            st.success("Observación grabada correctamente!")
            if img_file_buffer is not None:
                id = uuid.uuid1()
                # To read image file buffer as bytes:
                with open (f'{str(id)}.jpg','wb') as file:
                    file.write(img_file_buffer.getbuffer())
                bytes_data = img_file_buffer.getvalue()
            st.rerun()
            st.caching.clear_caching()

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