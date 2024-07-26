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
                                                      "padding": "14px"}})

        nav_bar_height = """
        <style>
            iframe:first-of-type{
                margin-top: -11.5rem;
            }
            [data-testid="collapsedControl"] {
                display: none
            }
            div[data-testid="stSidebarUserContent"]{
                padding-top: 0rem;
                margin-top: -3.3rem;
            }
            div[data-testid="stLogoSpacer"]{
                height: 0rem;
            }
            div[data-testid="stSidebarHeader"]{
                padding: 0rem; 
            }
            div[data-testid="stSidebarCollapseButton"]{
                display: block;
            }
            div[data-testid="collapsedControl"] {
                left: 0.3125rem;
                top: calc((1.875rem - 2rem) / 2);
            }
            div[data-testid="stToolbar"] {
                top: calc((1.875rem - 2rem) / 2);
                right: 0.3125rem;
            }
        </style>
        """
        st.markdown(nav_bar_height, unsafe_allow_html=True)
        # #root > div:nth-child(1) > div:nth-child(1) > div > div > div > section:nth-child(2) > div:nth-child(1) > div > div > div > div:nth-child(9){
        #         display: none;
        #     }

        for pg in self.pages:
            if selected_page == pg:
                page = self.pages[selected_page](self.auth)
                page.show()  
                break      