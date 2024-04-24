import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title('Comparte fruta')

location = streamlit_geolocation()

st.write(location)

