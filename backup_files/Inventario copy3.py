import streamlit as st
import pandas as pd
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from streamlit_extras.metric_cards import style_metric_cards
from nav_bar.st_sub_navbar import SubNavbar


class Inventario(AuthController, DataController):
    def __init__(self, auth):
        AuthController.__init__(self, auth)
        DataController.__init__(self)

    def show(self): 
        if "selected_option" not in st.session_state:
            st.session_state.selected_option = 0

        options = ["Dashboard","Resumen", "Edit Inventory"]
        icons = icons=['boxes','list-task', 'pencil']
        
        sub_navbar = SubNavbar(options, icons, st.session_state.selected_option)
        selected_option = sub_navbar.show()

        selected_index = options.index(selected_option)
        selected_index = options.index(selected_option)
        if st.session_state.selected_option != selected_index:
            st.session_state.selected_option = selected_index
            st.rerun()
        
        if selected_option in [options[0], None]:
            self.show_summary()
        elif selected_option == options[1]:
            self.show_current_totals()
        elif selected_option == options[2]:
            self.edit_inventory_item()

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

    def edit_inventory_item(self):
        part_number = -1
        is_disabled = True
        if 'operation' not in st.session_state:
            st.session_state.operation = 0
            st.session_state.part_number = None
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            operation = st.selectbox("Seleccionar o Ingresar No. Parte",
                                        options= ["Seleccionar existente", "Ingresar nuevo"])

            if operation == "Seleccionar existente":
                st.session_state.operation = 1
            elif operation == "Ingresar nuevo":
                st.session_state.operation = 2

        with col2:
            if st.session_state.operation == 0:
                st.warning('Select operation')
                st.selectbox("No. Parte", options= self.part_numbers, index=None, placeholder="Select", disabled=True)

            if st.session_state.operation == 1 :
                print(st.session_state.part_number)
                part_number = st.selectbox("No. Parte", 
                                           options= self.part_numbers, 
                                           index = st.session_state.part_number, 
                                           placeholder="Select")
                if part_number:
                    st.session_state.part_number = self.part_numbers.index(part_number)
                is_disabled = True

            elif st.session_state.operation == 2:
                part_number = st.text_input("No. Parte", placeholder= "Enter New Part Number")
                is_disabled = False
        
        col1,  _ = st.columns(2)
        with col1:
            if st.session_state.operation == 2 and part_number and int(part_number) in self.part_numbers: 
                st.error('Part Number Already Exists')  
                is_disabled = True          
        
        part_details = self.filter_by_part_number(part_number)
        st.markdown("### Detalles del Articulo")         

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            c1, c2 = st.columns(2)
            with c1:
                date = st.date_input("Fecha", 
                                value = pd.to_datetime("today"), 
                                format ="DD-MM-YYYY")
            with c2: 
                unidad = st.selectbox("Unidad", 
                                options=["Uno", "Par"], #one or pair
                                index=["Uno", "Par"].index(part_details["Unidad"]),
                                disabled= is_disabled)
            description = st.text_area("Descripcion", value=str(part_details["Descripcion"]), 
                                       height = 122, disabled= is_disabled)
        
        with col2:
            incoming_num_pieces = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=0)
            
            outgoing_num_pieces = st.number_input("Salida (Cantidad)", step=1, format="%d", value=0)
            
            part_loss = st.number_input("Perdida", step=1, format="%d", value=0)
        
        with col3:
            cost_per_unit = st.text_input("Costo por Unidad", 
                                          value=f"${part_details['Costo por Unidad']:.2f}", 
                                          disabled= is_disabled)
            cost_per_unit = float(cost_per_unit.replace('$', '')) if cost_per_unit.strip() != '' else 0.00

            current_num_pieces = incoming_num_pieces - outgoing_num_pieces - part_loss
            total_num_pieces = part_details['Existencia Actual'] + current_num_pieces
            current_stock_value = current_num_pieces * cost_per_unit
            total_stock_value = total_num_pieces * cost_per_unit

            st.number_input("Total Pieces", value=current_num_pieces, key="existencia_actual", disabled=True)
            
            st.metric(label="Total Valor", value=f"${current_stock_value:.2f}")

            
        cl1, cl2, cl3, cl4 = st.columns(4)
        with cl2:
            if st.button(label='Guardar', use_container_width=True, type= "primary"):
                if part_number:
                    self.save_data([date, description, part_number, unidad, cost_per_unit, incoming_num_pieces, outgoing_num_pieces, part_loss, total_num_pieces, total_stock_value, 0, pd.to_datetime("today")])
                    st.toast("Your data has been saved successfully", icon = "✅")
                else:
                    st.error('Part Number Cannot be Empty') 

        with cl3:
            if st.button(label='Reset', use_container_width=True, type = "primary"):
                st.session_state.part_number = None
                                

        cl1, cl2, cl3 = st.columns([1, 2, 1]) 
        with cl2:
            if st.button(label='Borrar', use_container_width=True, type = "secondary"):
                self.remove_data(part_number)
                st.toast("Data was deleted", icon = "🧺")
        
    


        
        
            

