import streamlit as st
from auth.st_auth_user import UserAuthenticator
from nav_bar.st_custom_navbar import Navbar

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")


_, col1, _ = st.columns([1, 2, 1])
with col1:
    auth = UserAuthenticator()

    if auth.authentication_status == False:
        st.error('Nombre de usuario o contrasena incorrectos')
    elif auth.authentication_status == None:
        st.warning('Por favor entre nombre de usuario y contrasena')

if auth.authentication_status:
    navbar = Navbar(auth)
    navbar.show()
