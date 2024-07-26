import streamlit as st
import pandas as pd
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from streamlit_option_menu import option_menu


class Inventario(AuthController, DataController):
    def __init__(self, auth):
        AuthController.__init__(self, auth)
        DataController.__init__(self)

    def show(self): 
        if "selected_index" not in st.session_state:
            st.session_state.selected_option = 0

        options = ["Current Inventory", "Edit Inventory", "Historical Log"]
        icons = icons=['list-task', 'pencil', "book"]
        selected_option = option_menu(None, options, 
                                      icons=icons, 
                                      menu_icon="cast", 
                                      default_index=st.session_state.selected_option, 
                                      orientation= "horizontal",
                                      styles={"container": {"width": "45rem"},
                                              "nav-link": {"text-align": "center", "font-family": "var(--font)"},
                                              "nav-link-selected": {"background-color": "green", "font-weight": "bold", "font-family": "var(--font)"}
                                              })
        
        for i in range(len(options)):
            if selected_option == options[i]:
                st.session_state.selected_option = i
        
        if selected_option in ["Current Inventory", None]:
            pass
        elif selected_option == "Edit Inventory":
            self.edit_inventory_item()
        elif selected_option == "Historical Log":
            pass
    
    def edit_inventory_item(self):
        part_number = -1
        is_disabled = None
        if 'operation' not in st.session_state:
            st.session_state.operation = 0
            st.session_state.part_number = 0
        
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
                part_number = st.selectbox("No. Parte", options= self.part_numbers, index=None, placeholder="Select")
                is_disabled = True

            elif st.session_state.operation == 2:
                part_number = st.text_input("No. Parte", placeholder= "Enter New Part Number")
                is_disabled = False
        
        with col3:
            if part_number and int(part_number) in self.part_numbers: 
                st.error('Part Number Already Exists')            
        
        part_details = self.filter_by_part_number(part_number)
        st.markdown("### Detalles del Articulo")         

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            date = st.date_input("Fecha", 
                            value = pd.to_datetime(part_details["Fecha"]), 
                            format ="DD-MM-YYYY")
            incoming_num_pieces = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=int(part_details["Entrada (Cantidad)"]))
            
            outgoing_num_pieces = st.number_input("Salida (Cantidad)", step=1, format="%d", value=int(part_details["Salida (Cantidad)"]))
        
        with col2:
            unidad = st.selectbox("Unidad", 
                                options=["Uno", "Par"], #one or pair
                                index=["Uno", "Par"].index(part_details["Unidad"]))
            cost_per_unit = st.text_input("Costo por Unidad", value=f"${part_details['Costo por Unidad']:.2f}")
            cost_per_unit = float(cost_per_unit.replace('$', '')) if cost_per_unit.strip() != '' else 0.00
            part_loss = st.number_input("Perdida", step=1, format="%d", value=int(part_details["Perdida"]))
        
        with col3:
            description = st.text_area("Descripcion", value=str(part_details["Descripcion"]), height = 122)
            

            c1, c2 = st.columns(2)
            with c1:
                initial_num_pieces = st.number_input("Existencia Inicial", step=1, format="%d", value=int(part_details["Existencia Inicial"]), disabled= True)
            
            with c2:
                current_num_pieces = initial_num_pieces + incoming_num_pieces - outgoing_num_pieces
                
                st.number_input("Existencia Actual", value=current_num_pieces, step=1, format="%d", key="existencia_actual", disabled=True)
                current_stock_value = current_num_pieces * cost_per_unit
                # st.text_input("Existencia Actual (Valor)", value=f"${current_stock_value:.2f}", key="valor_existencia_actual", disabled=True)
                st.metric(label="Existencia Actual (Valor)", value=f"${current_stock_value:.2f}")

            
        cl1, cl2, cl3, cl4 = st.columns(4)
        with cl2:
            if st.button(label='Guardar', use_container_width=True, type= "primary"):
                self.save_data([date, description, part_number, unidad, cost_per_unit, initial_num_pieces, incoming_num_pieces, outgoing_num_pieces, current_num_pieces, current_stock_value, part_loss, 0])
                st.toast("Your data has been saved successfully", icon = "✅")
        with cl3:
            if st.button(label='Borrar', use_container_width=True, type = "primary"):
                self.save_data([date, description, part_number, unidad, cost_per_unit, initial_num_pieces, incoming_num_pieces, outgoing_num_pieces, current_num_pieces, current_stock_value, part_loss, 1])
                st.toast("Data was deleted", icon = "🧺")
        
    


        
        
            

