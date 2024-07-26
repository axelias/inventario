import streamlit as st
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from streamlit_extras.metric_cards import style_metric_cards


class Resumen(AuthController, DataController):
    def __init__(self, auth):
        AuthController.__init__(self, auth)
        DataController.__init__(self)

    def show(self):
        col1, col2, col3 = st.columns(3)
        with col1:
            total_initial_inv = self.get_initial_investment()
            st.metric(label="Inventario Inicial", value=f"${total_initial_inv}", delta="8%")
        with col2:
            total_existing_inv = self.get_existing_investment()
            st.metric(label="Inventario Existente", value=f"${total_existing_inv}", delta="8%")
        with col3:
            total_sold_value = self.get_sold_value()
            st.metric(label="Inventario Existente", value=f"${total_sold_value}", delta="8%")
        style_metric_cards(border_left_color= 'green', box_shadow= False, background_color= "none") # ----- should turn red with delta is negative
        

    
           

    