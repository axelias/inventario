import streamlit as st
from auth.st_auth_user import UserAuthenticator
from nav_bar.st_custom_navbar import Navbar

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")


_, col1, _ = st.columns([1, 2, 1])
with col1:
    auth = UserAuthenticator()

    if auth.authentication_status == False:
        st.error('Username or password is incorrect')
    elif auth.authentication_status == None:
        st.warning('Please enter your username and password')

if auth.authentication_status:
    navbar = Navbar(auth)
    navbar.show()