import streamlit as st
from streamlit_option_menu import option_menu

class SubNavbar:
    def __init__(self, options, icons, default_index):
        self.options = options
        self.icons = icons
        self.default_index = default_index

    def show(self):
        selected_option = option_menu(None, 
                                options         = self.options, 
                                icons           = self.icons,  
                                default_index   = self.default_index, 
                                menu_icon       = "cast",
                                orientation     = "horizontal",
                                styles={"container":        {"padding": "5px"},
                                        
                                        "nav-link":         {"text-align": "center", 
                                                            "font-family": "var(--font)",
                                                            "padding": "10px 0px 0px 0px",#top right bottom left
                                                            "margin": "0px"},

                                        "nav-link-selected":{"text-align": "center",
                                                            "background-color": "green", 
                                                            "font-weight": "bold", 
                                                            "font-family": "var(--font)",
                                                            "padding": "10px 0px 10px 0px"},
                                })
        
        return selected_option

