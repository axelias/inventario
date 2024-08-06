import streamlit as st
import matplotlib.pyplot as plt
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

        options = ["Weekly Dashboard","Weekly Sales", "Historical Log"] #, 
        icons = icons=['boxes','receipt-cutoff', 'book']
        
        sub_navbar = SubNavbar(options, icons, st.session_state.selected_option)
        selected_option = sub_navbar.show()

        
        for i in range(len(options)):
            if selected_option == options[i]:
                st.session_state.selected_option = i
        
        if selected_option in [options[0], None]:
            self.show_total_weekly_sales()
        elif selected_option == options[1]:
            self.show_weekly_sales_graph()
        elif selected_option == options[2]:
            self.show_history()

    def show_total_weekly_sales(self):
        total_weekly_sales, total_weekly_sales_amount = self.get_total_weekly_sales()
        total_weekly_losses, total_weekly_losses_amount = self.get_total_weekly_losses()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            
            st.metric(label="Total Weekly Sales", value=f"{total_weekly_sales} Units", delta="8%")
        with col2:
            st.metric(label="Total Weekly Sales Amount", value=f"${total_weekly_sales_amount}", delta="8%")
        with col3:
            st.metric(label="Total Week Losses", value=f"{total_weekly_losses} Units", delta="8%")
        with col4:
            st.metric(label="Total Week Losses Amount", value=f"${total_weekly_losses_amount}", delta="8%")
        style_metric_cards(border_left_color= 'green', box_shadow= False, background_color= "none")

    def show_weekly_sales_graph(self):
        col1, col2 = st.columns(2)
        with col1:
            weekly_overall_graph = self.get_weekly_sales_loss_graph(title = 'Sales vs Loss Per Day')
            st.altair_chart(weekly_overall_graph, use_container_width=True)

        with col2:
            c1, c2 = st.columns(2)
            with c1:
                weekly_sales_graph = self.get_weekly_sales_graph(title = 'Sales Per Day')
                st.altair_chart(weekly_sales_graph, use_container_width=True)
            with c2:
                weekly_loss_graph = self.get_weekly_loss_graph(title = 'Loss Per Day')
                st.altair_chart(weekly_loss_graph, use_container_width=True)



    def show_history(self):
        st.header('Data History Log')
        history = self.get_history()
        st.data_editor(history, disabled = True, use_container_width=True)
