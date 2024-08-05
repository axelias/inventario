# import streamlit as st
# from streamlit_navigation_bar import st_navbar

# page = st_navbar(["Resumen", "Ventas", "Inventario", "Log Out"])
# st.write(page)

import streamlit as st
from streamlit_navigation_bar import st_navbar
from config.page_config import pages
from config.style_config import css_style

class Navbar():
    def __init__(self, auth):
        self.pages = pages
        self.page_names = list(self.pages.keys())
        self.auth = auth
    

    def show(self):
        selected_page = st_navbar(self.page_names,
                                  options = {"use_padding":False}, 
                                  styles = {"nav": {"padding-left": "0px",
                                                    "padding-right": "0px"},
                                            "active":  {"background-color": "green",
                                                      "color": "white",
                                                      "padding": "14px",
                                                      }},
                                  selected=self.page_names[0])

        st.markdown(css_style, unsafe_allow_html=True)
        for pg in self.pages:
            if selected_page == pg:
                page = self.pages[selected_page](self.auth)
                page.show()  
                break      