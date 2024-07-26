import streamlit as st
import pandas as pd
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from streamlit_extras.metric_cards import style_metric_cards


class Resumen(AuthController, DataController):
    def __init__(self, auth):
        AuthController.__init__(self, auth)
        DataController.__init__(self)

    def show(self):
        self.show_content()
        self.show_sidebar()

    def show_content(self):
        # st.title('Inventario para Ventas')
        col1, col2 = st.columns([3, 1])
        with col1:
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="Inventario Inicial", value=f"${self.initial_inv}", delta="8%")
            with c2:
                st.metric(label="Inventario Existente", value=f"${self.current_inv}", delta="8%")
            st.header('Datos Actuales')
            st.dataframe(self.data)
        with col2:
            self.show_sidebar()
        # style_metric_cards(border_left_color= 'green', box_shadow= False) # ----- should turn red with delta is negative
        

    def show_sidebar(self): 
        st.markdown(
            """
            [data-testid="stSidebarHeader"] {
                padding: 0rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # with st.sidebar:        
        st.header("Detalles del Articulo")
        part_number = self.get_part_number()
        part_details = self.filter_by_part_number(part_number)
        part_details = self.get_new_part_details(part_details)
            # if option in [1, 2]:
            #     part_details = self.filter_by_part_number(part_number)
                # self.get_new_part_details(part_details)

    def get_part_number(self):
        # st.write("Seleccionar o Ingresar No. Parte")
        st.markdown(
            """
            <style>
            button {
                height: 50px;  /* Set the height here */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        part_number = -1
        if 'option' not in st.session_state:
            st.session_state.option = 0
            st.session_state.part_number = 0
        c1_sub, c2_sub = st.columns(2)

        with c1_sub:
            if st.button("Seleccionar existente", key='select'):
                st.session_state.option = 1
        with c2_sub:
            if st.button("Ingresar nuevo", key='new'):
                st.session_state.option = 2   
        
        if st.session_state.option == 0:
            st.warning('Select operation')
            st.selectbox("No. Parte", options= self.part_numbers, index=None, placeholder="Select", disabled=True)

        if st.session_state.option == 1 :
            part_number = st.selectbox("No. Parte", options= self.part_numbers, index=None, placeholder="Select")
            # print('part number:', part_number)
            # if not part_number:
            #     st.warning('Enter or Select Part Number')
   
        elif st.session_state.option == 2:
            part_number = st.text_input("No. Parte", placeholder= "Enter New Part Number")
            # print('part number:', part_number)

            # if not part_number:
            #     st.warning('Enter a New Part Number')
            if part_number and int(part_number) in self.part_numbers: #supposing part numbers are integers
                st.error('Part Number Already Exists')            
            
        # if st.session_state.option in [1, 2]:
            # st.session_state.part_number = part_number
        return part_number
    
    def get_new_part_details(self, part_details):
        with st.sidebar.expander("Detalles de Inventario", expanded=True):
            date = st.date_input("Fecha", 
                            value = pd.to_datetime(part_details["Fecha"]), 
                            format ="DD-MM-YYYY")
            description = st.text_input("Descripcion", value=str(part_details["Descripcion"]))
            unidad = st.selectbox("Unidad", 
                                options=["Uno", "Par"],             #one or pair
                                index=["Uno", "Par"].index(part_details["Unidad"]))
            cost_per_unit = st.text_input("Costo por Unidad", value=f"${part_details['Costo por Unidad']:.2f}")
            cost_per_unit = float(cost_per_unit.replace('$', '')) if cost_per_unit.strip() != '' else 0.00
            
            initial_num_pieces = st.number_input("Existencia Inicial", step=1, format="%d", value=int(part_details["Existencia Inicial"]))

            incoming_num_pieces = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=int(part_details["Entrada (Cantidad)"]))
            
            outgoing_num_pieces = st.number_input("Salida (Cantidad)", step=1, format="%d", value=int(part_details["Salida (Cantidad)"]))

            current_num_pieces = initial_num_pieces + incoming_num_pieces - outgoing_num_pieces
            
            st.number_input("Existencia Actual", value=current_num_pieces, step=1, format="%d", key="existencia_actual", disabled=True)

            current_stock_value = current_num_pieces * cost_per_unit
            st.text_input("Existencia Actual (Valor)", value=f"${current_stock_value:.2f}", key="valor_existencia_actual", disabled=True)

            part_loss = st.number_input("Perdida", step=1, format="%d", value=int(part_details["Perdida"]))


            #form a dataframe to return 

        return part_details
    

