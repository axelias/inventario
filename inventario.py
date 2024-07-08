import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import os
from babel.dates import format_date
import locale

# Set the width of the Streamlit page
st.set_page_config(layout="wide")

# Define the path to the Excel file
excel_file = 'data.xlsx'

# Authentication credentials
Usuario = "inv247"
Contrasena = "inv247"

# Authenticate users
def authenticate(username, password):
    return username == Usuario and password == Contrasena

# Streamlit app
# Session state to track authentication status
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Logout button
if st.session_state.authenticated:
    salir = st.sidebar.button("Salir")
    if salir:
        st.session_state.authenticated = False

# Authentication form and main content
if not st.session_state.authenticated:
    st.title("")  # Setting an empty title
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    entrar = st.sidebar.button("Entrar")

    if entrar:
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.sidebar.success("¡Inicio de sesión exitoso!")
        else:
            st.sidebar.error("Credenciales incorrectas. Inténtelo de nuevo.")

# Proceed only if authenticated
if st.session_state.authenticated:
    st.title("Inventario para Ventas")  # Displaying the title only when authenticated
    
    # Load existing data to get "No. Parte" values
    try:
        df_current = pd.read_excel(excel_file, engine='openpyxl')  # Explicitly specify engine here
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        df_current = pd.DataFrame()  # Initialize an empty DataFrame

    # Convert currency columns to float after removing dollar signs
    df_current["Salida (Valor)"] = df_current["Salida (Valor)"].replace('[\$,]', '', regex=True).astype(float)
    df_current["Existencia Final (Valor)"] = df_current["Existencia Final (Valor)"].replace('[\$,]', '', regex=True).astype(float)

    total_existencia_inicial_valor = df_current["Salida (Valor)"].sum()
    total_existencia_final_valor = df_current["Existencia Final (Valor)"].sum()

    # Display running totals as metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Existencia Inicial (Valor)", value=f"${total_existencia_inicial_valor:.2f}")
    with col2:
        st.metric(label="Total Existencia Final (Valor)", value=f"${total_existencia_final_valor:.2f}")

    no_parte_values = df_current["No. Parte"].dropna().unique().tolist()

    # Select or input new "No. Parte" in the sidebar
    st.sidebar.header("Detalles del Articulo")
    no_parte_selection = st.sidebar.selectbox("Seleccionar o Ingresar No. Parte", options=["Seleccionar existente"] + no_parte_values + ["Ingresar nuevo"])
    if no_parte_selection == "Ingresar nuevo":
        no_parte = st.sidebar.text_input("No. Parte", "")
    elif no_parte_selection == "Seleccionar existente":
        no_parte = st.sidebar.selectbox("No. Parte", options=no_parte_values)
    else:
        no_parte = no_parte_selection

    # Function to get current data for a selected part number
    def get_current_data(part_number):
        if part_number in no_parte_values:
            return df_current[df_current["No. Parte"] == part_number].iloc[0]
        return pd.Series({
            "Fecha": pd.to_datetime("today"),
            "Descripcion": "",
            "Unidad": "Uno",
            "Costo p/ Unidad": "$0.00",
            "Existencia Inicial": 0,
            "Existencia Inicial (Valor)": "$0.00",
            "Entrada (Cantidad)": 0,
            "Entrada (Valor)": "$0.00",
            "Salida (Cantidad)": 0,
            "Salida (Valor)": "$0.00",
            "Existencia Final": 0,
            "Existencia Final (Valor)": "$0.00",
            "Perdida": 0
        })

    current_data = get_current_data(no_parte)

    # Set the locale to Spanish
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        st.warning("Locale setting failed. Default locale will be used.")

    # Input fields in the sidebar
    with st.sidebar.expander("Detalles de Inventario", expanded=True):
        fecha = st.date_input("Fecha", pd.to_datetime(current_data["Fecha"]), format="DD-MM-YYYY")
        fecha_str = fecha.strftime('%d de %B de %Y')

        descripcion = st.text_input("Descripcion", value=str(current_data["Descripcion"]))

        unidad = st.selectbox("Unidad", options=["Uno", "Par"], index=["Uno", "Par"].index(current_data["Unidad"]))
        
        # Remove dollar sign for conversion to float
        costo_por_unidad = st.number_input("Costo p/ Unidad", format="%.2f", value=float(str(current_data.get("Costo p/ Unidad", "0.00")).replace('$', '')))
        
        existencia_inicial = st.number_input("Existencia Inicial", step=1, format="%d", value=int(current_data["Existencia Inicial"]))

        valor_existencia_inicial = existencia_inicial * costo_por_unidad
        st.text_input("Entrada (Valor)", value=f"${valor_existencia_inicial:.2f}", key="valor_existencia_inicial", disabled=True)
        
        cantidad_entrada = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=int(current_data["Entrada (Cantidad)"]))

        # Ensure numeric inputs handle None gracefully
        def get_int_value(value):
            return int(value) if pd.notna(value) else 0

        valor_entrada = cantidad_entrada * costo_por_unidad
        st.text_input("Entrada (Valor)", value=f"${valor_entrada:.2f}", key="valor_entrada", disabled=True)

        cantidad_salida = st.number_input("Salida (Cantidad)", step=1, format="%d", value=get_int_value(current_data.get("Salida (Cantidad)")))
        
        valor_salida = cantidad_salida * costo_por_unidad
        st.text_input("Salida (Valor)", value=f"${valor_salida:.2f}", key="valor_salida", disabled=True)

        existencia_final = st.number_input("Existencia Final", step=1, format="%d", value=get_int_value(current_data.get("Existencia Final")))
        
        valor_existencia = existencia_final * costo_por_unidad
        st.text_input("Existencia (Valor)", value=f"${valor_existencia:.2f}", key="valor_existencia", disabled=True)

        perdida = st.number_input("Perdida", step=1, format="%d", value=get_int_value(current_data.get("Perdida")))

        if st.button("Guardar"):
            # Create a new DataFrame with the input data
            new_data = pd.DataFrame({
                "Fecha": [fecha.strftime('%d/%m/%Y')],
                "Descripcion": [descripcion],
                "No. Parte": [no_parte],
                "Unidad": [unidad],
                "Existencia Inicial": [existencia_inicial],
                "Existencia Inicial (Valor)": [f"${valor_existencia_inicial:.2f}"],
                "Entrada (Cantidad)": [cantidad_entrada],
                "Entrada (Valor)": [f"${valor_entrada:.2f}"],
                "Salida (Cantidad)": [cantidad_salida],
                "Salida (Valor)": [f"${valor_salida:.2f}"],
                "Existencia Final": [existencia_final],
                "Existencia Final (Valor)": [f"${valor_existencia:.2f}"],
                "Perdida": [perdida]
            })

            # Write data to Excel, overwriting existing sheet
            try:
                with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
                    new_data.to_excel(writer, index=False, header=True, sheet_name='Sheet1')
                st.sidebar.success("¡Datos guardados exitosamente!")
            except Exception as e:
                st.sidebar.error(f"Error saving data: {e}")

    # Display the current data in the Excel file in the main page
    st.header("Datos Actuales")
    try:
        df_current = pd.read_excel(excel_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        df_current = pd.DataFrame()  # Initialize an empty DataFrame

    # Editable data grid in the main page
    gb = GridOptionsBuilder.from_dataframe(df_current)
    gb.configure_default_column(editable=True)
    gridOptions = gb.build()

    # Function to customize grid options
    def customize_grid(grid_response):
        # Auto-size all columns
        grid_response['gridOptions']['suppressAutoSize'] = False
        grid_response['gridOptions']['autoSizeColumns'] = True
        return grid_response

    grid_response = AgGrid(
        df_current,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        width='100%',  # Adjust width of the AgGrid component
        data_return_level='AS_INPUT',
        on_ready=customize_grid
    )

    # Get edited data
    df_edited = pd.DataFrame(grid_response['data'])

    if st.button("Actualizar Datos"):
        try:
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
                df_edited.to_excel(writer, index=False)
            st.success("¡Datos actualizados exitosamente!")
        except Exception as e:
            st.error(f"Error updating data: {e}")
