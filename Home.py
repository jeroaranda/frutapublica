import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import plotly.express as px
from database_utils import (
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
    page = st.sidebar.radio("Navigate", ["Map View", "Share Flora", "Recipes", "Analytics"])
    
    if page == "Map View":
        show_map_view()
    elif page == "Share Flora":
        share_flora()
    elif page == "Recipes":
        show_recipes()
    elif page == "Analytics":
        show_analytics()

def show_map_view():
    st.header("Flora Map")
    
    df = get_observations_df()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Observations:", len(df))
    col2.metric("Unique Flora:", df['flora_name'].nunique())
    col3.metric("Active Users:", df['username'].nunique())
    
    # Create map
    df['size'] = 0.5
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size='size',
        color="flora_name",
        mapbox_style="carto-positron",
        zoom=0.7,
        hover_data=["id", "flora_name", "username", "description"]
    )
    fig.update_traces(cluster=dict(enabled=True))
    st.plotly_chart(fig, use_container_width=True)

def share_flora():
    st.header("Share Flora")
    
    session = get_db_session()
    flora_options = [f.name for f in session.query(Flora).all()] + ["Other..."]
    user_options = [u.username for u in session.query(User).all()] + ["Other..."]
    session.close()
    
    # Form inputs
    flora = st.selectbox("Flora:", options=flora_options)
    if flora == "Other...":
        flora = st.text_input("Add new flora name:")
    
    username = st.selectbox("Username:", options=user_options)
    if username == "Other...":
        username = st.text_input("Add new username:")
    
    # Get location
    location = streamlit_geolocation()
    if location['latitude'] is not None:
        lat = location["latitude"]
        lon = location["longitude"]
        st.write(f"Your location: ({lat}, {lon})")
    else:
        location_input = st.text_input("Add location (latitude,longitude):")
        try:
            lat, lon = map(float, location_input.split(','))
        except:
            lat = lon = None
    
    address = st.text_input("Address (optional):")
    description = st.text_area("Observations:")
    
    if st.button("Submit", type="primary"):
        if all([flora, username, lat, lon]):
            add_observation(flora, username, lat, lon, address, description)
            st.success("Observation recorded successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields.")

def show_recipes():
    st.header("Flora Recipes")
    
    # Tab selection
    tab1, tab2 = st.tabs(["Browse Recipes", "Add Recipe"])
    
    with tab1:
        recipes = get_recipes()
        for recipe in recipes:
            with st.expander(recipe['name']):
                st.write("**Ingredients:**")
                for ingredient in recipe['ingredients']:
                    st.write(f"- {ingredient}")
                st.write("\n**Preparation:**")
                st.write(recipe['prep'])
    
    with tab2:
        st.subheader("Add New Recipe")
        
        name = st.text_input("Recipe Name:")
        
        session = get_db_session()
        available_flora = [f.name for f in session.query(Flora).all()]
        session.close()
        
        ingredients = st.multiselect("Ingredients:", available_flora)
        prep = st.text_area("Preparation Instructions:")
        
        if st.button("Add Recipe"):
            if name and ingredients and prep:
                add_recipe(name, prep, ingredients)
                st.success("Recipe added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all fields.")

def show_analytics():
    st.header("Analytics")
    
    df = get_observations_df()
    
    # Flora distribution
    fig1 = px.bar(
        df['flora_name'].value_counts().reset_index(),
        x='index',
        y='flora_name',
        title='Flora Distribution',
        labels={'index': 'Flora Type', 'flora_name': 'Count'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # User activity
    fig2 = px.bar(
        df['username'].value_counts().reset_index(),
        x='index',
        y='username',
        title='User Activity',
        labels={'index': 'User', 'username': 'Observations'}
    )
    st.plotly_chart(fig2, use_container_width=True)

if __name__ == '__main__':
    main()