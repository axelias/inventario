import streamlit as st
import pandas as pd
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from streamlit_extras.metric_cards import style_metric_cards
from nav_bar.st_sub_navbar import SubNavbar


class Ventas(AuthController, DataController):
    def __init__(self, auth):
        AuthController.__init__(self, auth)
        DataController.__init__(self)

    def show(self): 
        if "selected_index" not in st.session_state:
            st.session_state.selected_option = 0

        options = ["Dashboard","Resumen", "Historical Log"] #, 
        icons = icons=['boxes','list-task', 'book']
        
        sub_navbar = SubNavbar(options, icons, st.session_state.selected_option)
        selected_option = sub_navbar.show()

        
        for i in range(len(options)):
            if selected_option == options[i]:
                st.session_state.selected_option = i
        
        if selected_option in [options[0], None]:
            self.show_summary()
        elif selected_option == options[1]:
            self.show_current_totals()
        elif selected_option == options[2]:
            self.show_history()

    def show_summary(self):
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
        style_metric_cards(border_left_color= 'green', box_shadow= False, background_color= "none")

    def show_current_totals(self):
        st.header('Data Inventory Totals')
        st.data_editor(self.totals_summary, disabled = True, use_container_width=True)
    
    def show_history(self):
        st.header('Data History Log')
        history = self.get_history()
        st.data_editor(history, disabled = True, use_container_width=True)
