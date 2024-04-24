import streamlit as st
from streamlit_geolocation import streamlit_geolocation

st.title('Comparte fruta')

# Layout for the form 
with st.form("myform"):

    "### A form"

    # These exist within the form but won't wait for the submit button
    placeholder_for_selectbox = st.empty()
    placeholder_for_optional_text = st.empty()

    location = streamlit_geolocation()
    if 'latitude' in location:
        st.write(f'Your location is (lat:{location["latitude"]},lon:{location["longitude"]})')
    img_file_buffer = st.camera_input("Toma una foto")

    if img_file_buffer is not None:
        # To read image file buffer as bytes:
        bytes_data = img_file_buffer.getvalue()
        # Check the type of bytes_data:
        # Should output: <class 'bytes'>
        st.write(type(bytes_data))

    
    submit_button = st.form_submit_button("Submit!")

    

    # Create selectbox
    with placeholder_for_selectbox:
        options = ['limón','mango','mandarina','gasparito'] + ["Another option..."]
        selection = st.selectbox("Selecciona una opción", options=options)

    # Create text input for user entry
    with placeholder_for_optional_text:
        if selection == "Otra opción...":
            otherOption = st.text_input("Añade tu opción...")

    


