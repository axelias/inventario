# import streamlit as st
# from streamlit_navigation_bar import st_navbar

# page = st_navbar(["Resumen", "Ventas", "Inventario", "Log Out"])
# st.write(page)

import streamlit as st
from streamlit_navigation_bar import st_navbar
from config.page_config import pages

class Navbar(object):
    def __init__(self, auth):
        self.pages = pages
        self.page_names = list(self.pages.keys())
        self.auth = auth
    

    def show(self):
        selected_page = st_navbar(self.page_names,
                                  options = {"use_padding":False}, 
                                  styles = {"active":  {"background-color": "green",
                                                      "color": "white",
                                                      "padding": "14px"}},
                                  selected=self.page_names[0])
        


        nav_bar_height = """
        <style>
            iframe:first-of-type{
                margin-top: -11.5rem;
            }
            button[data-testid="baseButton-primary"]{
                background-color: #f0f2f6;
                border: 1px solid green;
                color: black;
            }
            button[data-testid="baseButton-primary"]:hover{
                background-color: green;
                color: white;
                border: none;
            }
        </style>
        """
        st.markdown(nav_bar_height, unsafe_allow_html=True)
        for pg in self.pages:
            if selected_page == pg:
                page = self.pages[selected_page](self.auth)
                page.show()  
                break      