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

        options = ["Panel","Resumen", "Editar Inventario"]
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
            st.metric(label="Inventario Inicial", value=f"${total_initial_inv}")
        with col2:
            total_existing_inv = self.get_existing_investment()
            st.metric(label="Inventario Existente", value=f"${total_existing_inv}")
        with col3:
            total_sold_value = self.get_sold_value()
            st.metric(label="Inventario Vendido", value=f"${total_sold_value}")
        style_metric_cards(border_left_color= 'green', box_shadow= False, background_color= "none")

    def show_current_totals(self):
        st.header('Totales en Inventario')
        st.data_editor(self.totals_summary, disabled = True, use_container_width=True)

    def edit_inventory_item(self):
        if 'del_toast' not in st.session_state:
            st.session_state.del_toast = False

        if 'reset' not in st.session_state:
            st.session_state.reset = False

        if 'part_empty_error' not in st.session_state:
            st.session_state.part_empty_error = False

        if 'operation' not in st.session_state:
            st.session_state.operation = 0

        if st.session_state.del_toast == True:
            st.toast("Datos borrados", icon = "🧺")
            st.session_state.del_toast = False
        
        @st.experimental_dialog('Confirmación de Eliminación')
        def show_dialog():
            st.write("Desea borrar este articulo?")
            st.text_input("No. Parte", value = part_number, disabled = True)          
            st.text_input("Descripcion", value = description, disabled = True)
            col1, col2 = st.columns(2)
            with col1: 
                if st.button('Si', use_container_width=True, type = "secondary"):
                    self.remove_data(part_number)
                    st.session_state.del_toast = True
                    st.session_state.del_part_number = None
                    st.rerun()
            with col2:
                if st.button('No', use_container_width=True, type = "primary"):
                    st.session_state.del_part_number = None
                    st.rerun()


        # def reset_form():
        if st.session_state.reset:
            st.session_state.select_part_number = None
            st.session_state.del_part_number = None
            st.session_state.new_part_number = None
            st.session_state.entrada = 0
            st.session_state.perdida = 0
            st.session_state.salida = 0
            st.session_state.fecha = pd.to_datetime("today")
            st.session_state.description = ''
            if st.session_state.operation == 2:
                st.session_state.cost_per_unit = '$0.00'
            st.session_state.reset = False
            st.rerun()
        
        part_number = None
        is_disabled = True
        is_completely_disabled = False
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            options = ["Seleccionar existente", "Ingresar nuevo", "Borrar existente"]
            operation = st.selectbox("Seleccionar Operacion",
                                        options = options, index = None, placeholder= "Seleccione una Opcion")

            if operation == options[0]:
                st.session_state.operation = 1
            elif operation == options[1]:
                st.session_state.operation = 2
            elif operation == options[2]:
                st.session_state.operation = 3
        
        with col2:
            if st.session_state.operation == 0:
                st.selectbox("No. Parte", options= self.part_numbers, index=None, placeholder="Seleccionar", disabled=True)

            if st.session_state.operation == 1 :
                part_number = st.selectbox("No. Parte", 
                                           options= self.part_numbers, 
                                           index = None,
                                           key = 'select_part_number',
                                           placeholder="Seleccionar")

            if st.session_state.operation == 2:
                part_number = st.text_input("No. Parte", placeholder= "Entre nuevo numero de parte", key = 'new_part_number')
                is_disabled = False

            if st.session_state.operation == 3 :
                part_number = st.selectbox("No. Parte", 
                                           options= self.part_numbers, 
                                           index = None,
                                           key = 'del_part_number',
                                           placeholder="Seleccionar")
                is_completely_disabled = True
                
        
        col1,  _ = st.columns(2)
        with col1:
            if st.session_state.operation == 0:
                st.warning('Seleccionar Operacion')
            if st.session_state.operation == 2 and part_number and int(part_number) in self.part_numbers: 
                st.error('El Número de Parte Ya Existe')  
                is_disabled = True      
            if st.session_state.part_empty_error == True:
                st.error('El Número de Parte No Puede Estar Vacío')  
                st.session_state.part_empty_error = False
        
        part_details = self.filter_by_part_number(part_number)
        if st.session_state.operation == 3 :
            part_details = self.fitler_summary_by_part_number(part_number)

        st.markdown("### Detalles del Articulo")         

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            c1, c2 = st.columns(2)
            with c1:
                date = st.date_input("Fecha", 
                                # value = part_details['Fecha'], 
                                format ="DD-MM-YYYY",
                                disabled = is_completely_disabled,
                                key = 'fecha')
            with c2: 
                unidad = st.selectbox("Unidad", 
                                options=["Uno", "Par"], #one or pair
                                index=["Uno", "Par"].index(part_details["Unidad"]),
                                disabled= is_disabled)
            description = st.text_area("Descripcion", value=str(part_details["Descripcion"]), 
                                       height = 122, disabled = is_disabled, key='description')
        
        with col2:
            incoming_num_pieces = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=part_details["Entrada (Cantidad)"] if st.session_state.operation == 3 else 0, disabled = is_completely_disabled, key='entrada')
            
            outgoing_num_pieces = st.number_input("Salida (Cantidad)", step=1, format="%d", value=part_details["Salida (Cantidad)"] if st.session_state.operation == 3 else 0, disabled = is_completely_disabled, key='salida')
            
            part_loss = st.number_input("Perdida", step=1, format="%d", value=part_details["Perdida"] if st.session_state.operation == 3 else 0, disabled = is_completely_disabled, key='perdida')
        
        with col3:
            cost_per_unit = st.text_input("Costo por Unidad", 
                                          value=f"${part_details['Costo por Unidad']:.2f}", 
                                          disabled = is_disabled, key='cost_per_unit')
            cost_per_unit = float(cost_per_unit.replace('$', '')) if cost_per_unit.strip() != '' else 0.00

            current_num_pieces = incoming_num_pieces - outgoing_num_pieces - part_loss
            total_num_pieces = part_details['Existencia Actual'] + current_num_pieces
            current_stock_value = current_num_pieces * cost_per_unit
            total_stock_value = total_num_pieces * cost_per_unit

            st.number_input("Articulos Totales", value=current_num_pieces, key="existencia_actual", disabled=True)
            
            st.metric(label="Valor Total", value=f"${current_stock_value:.2f}")

  
        cl1, cl2, cl3, cl4 = st.columns(4)
        with cl2:
            if st.session_state.operation in [0, 1, 2]:  
                if st.button(label='Guardar', use_container_width=True, type= "primary"):
                    if part_number:
                        self.save_data([date, description, part_number, unidad, cost_per_unit, incoming_num_pieces, outgoing_num_pieces, part_loss, total_num_pieces, total_stock_value, 0, pd.to_datetime("today")])
                        st.toast("Sus datos se han guardado correctamente", icon = "✅")
                    else:
                        st.session_state.part_empty_error = True
                        st.rerun()

                        
            elif st.session_state.operation == 3 :
                if st.button(label='Borrar', use_container_width=True, type = "secondary"):
                    if part_number:
                        show_dialog()
                    else:
                        st.session_state.part_empty_error = True
                        st.rerun()

        with cl3:
            st.button(label='Resetear', use_container_width=True, type = "primary", on_click=lambda: st.session_state.update({"reset": True}))

            



    
        
            

