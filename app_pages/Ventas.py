import streamlit as st
from controllers.auth_controller import AuthController

class Ventas(AuthController):
    def show(self):
        st.write("Ventas")