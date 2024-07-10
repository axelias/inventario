import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Set the width of the Streamlit page
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Define the path to the Excel file
excel_file = 'data.xlsx'

# Authentication credentials
Usuario = "inv247"
Contrasena = "inv247"

# Authenticate users
def authenticate(username, password):
    return username == Usuario and password == Contrasena

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
    currency_columns = ["Existencia Inicial (Valor)", "Existencia Actual (Valor)"]
    for col in currency_columns:
        df_current[col] = df_current[col].replace('[\$,]', '', regex=True).astype(float)

    total_existencia_inicial_valor = df_current["Existencia Inicial (Valor)"].sum()
    total_existencia_actual_valor = df_current["Existencia Actual (Valor)"].sum()

    # Display running totals as metrics
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric(label="Inventario Inicial", value=f"${total_existencia_inicial_valor:.2f}")

    with col2:
        st.metric(label="Inventario Existente", value=f"${total_existencia_actual_valor:.2f}")


    no_parte_values = df_current["No. Parte"].dropna().unique().tolist()

    # Select or input new "No. Parte" in the sidebar
    st.sidebar.header("Detalles del Articulo")
    
    no_parte_selection = st.sidebar.selectbox("Seleccionar o Ingresar No. Parte", options=["Seleccionar existente"] + no_parte_values + ["Ingresar nuevo"])
    
    if no_parte_selection in ["Ingresar nuevo", "Seleccionar existente"]:
        no_parte = st.sidebar.text_input("No. Parte", "") if no_parte_selection == "Ingresar nuevo" else st.sidebar.selectbox("No. Parte", options=no_parte_values)
    else:
        no_parte = no_parte_selection

    # Function to get current data for a selected part number
    def get_current_data(part_number):
        if part_number in no_parte_values:
            return df_current[df_current["No. Parte"] == part_number].iloc[0]
        return pd.Series({
            "Fecha": pd.to_datetime("today"),
            "Descripcion": "",
            "No. Parte": "",
            "Unidad": "Uno",
            "Costo por Unidad": 0.00,  # Default to 0.00 for float conversion
            "Existencia Inicial": 0,
            "Existencia Inicial (Valor)": 0.00,  # Default to 0.00 for float conversion
            "Entrada (Cantidad)": 0,
            "Entrada (Valor)": 0.00,  # Default to 0.00 for float conversion
            "Salida (Cantidad)": 0,
            "Existencia Actual": 0,
            "Existencia Actual (Valor)": 0.00,  # Default to 0.00 for float conversion
            "Perdida": 0
        })

    current_data = get_current_data(no_parte)

    # Input fields in the sidebar
    with st.sidebar.expander("Detalles de Inventario", expanded=True):
        
        fecha = st.date_input("Fecha", pd.to_datetime(current_data["Fecha"]), format="DD-MM-YYYY")
        descripcion = st.text_input("Descripcion", value=str(current_data["Descripcion"]))

        unidad = st.selectbox("Unidad", options=["Uno", "Par"], index=["Uno", "Par"].index(current_data["Unidad"]))
        
        costo_por_unidad_str = st.text_input("Costo por Unidad", value=f"${current_data['Costo por Unidad']:.2f}")
        costo_por_unidad = float(costo_por_unidad_str.replace('$', '')) if costo_por_unidad_str.strip() != '' else 0.00
        
        existencia_inicial = st.number_input("Existencia Inicial", step=1, format="%d", value=int(current_data["Existencia Inicial"]))

        cantidad_entrada = st.number_input("Entrada (Cantidad)", step=1, format="%d", value=int(current_data["Entrada (Cantidad)"]))
        
        cantidad_salida = st.number_input("Salida (Cantidad)", step=1, format="%d", value=int(current_data["Salida (Cantidad)"]))

        existencia_actual_calculated = existencia_inicial + cantidad_entrada - cantidad_salida
        
        st.number_input("Existencia Actual", value=existencia_actual_calculated, step=1, format="%d", key="existencia_actual", disabled=True)

        valor_existencia_actual_calculated = existencia_actual_calculated * costo_por_unidad
        st.text_input("Existencia Actual (Valor)", value=f"${valor_existencia_actual_calculated:.2f}", key="valor_existencia_actual", disabled=True)

        perdida = st.number_input("Perdida", step=1, format="%d", value=int(current_data["Perdida"]))

        if st.button("Guardar"):
            # Create a new DataFrame with the input data
            if no_parte in no_parte_values:
                # Update existing row
                idx = df_current.index[df_current["No. Parte"] == no_parte].tolist()
                if idx:
                    idx = idx[0]
                    df_current.loc[idx, "Fecha"] = fecha.strftime('%d/%m/%Y')
                    df_current.loc[idx, "Descripcion"] = descripcion
                    df_current.loc[idx, "Unidad"] = unidad
                    df_current.loc[idx, "Costo por Unidad"] = costo_por_unidad
                    df_current.loc[idx, "Existencia Inicial"] = existencia_inicial
                    df_current.loc[idx, "Existencia Inicial (Valor)"] = f"${existencia_inicial * costo_por_unidad:.2f}"
                    df_current.loc[idx, "Entrada (Cantidad)"] = cantidad_entrada
                    df_current.loc[idx, "Salida (Cantidad)"] = cantidad_salida
                    df_current.loc[idx, "Existencia Actual"] = existencia_actual_calculated
                    df_current.loc[idx, "Existencia Actual (Valor)"] = f"${valor_existencia_actual_calculated:.2f}"
                    df_current.loc[idx, "Perdida"] = perdida
            else:
                # Append new row
                new_data = pd.DataFrame({
                    "Fecha": [fecha.strftime('%d/%m/%Y')],
                    "Descripcion": [descripcion],
                    "No. Parte": [no_parte],
                    "Unidad": [unidad],
                    "Costo por Unidad": [costo_por_unidad],
                    "Existencia Inicial": [existencia_inicial],
                    "Existencia Inicial (Valor)": [f"${existencia_inicial * costo_por_unidad:.2f}"],
                    "Entrada (Cantidad)": [cantidad_entrada],
                    "Salida (Cantidad)": [cantidad_salida],
                    "Existencia Actual": [existencia_actual_calculated],
                    "Existencia Actual (Valor)": [f"${valor_existencia_actual_calculated:.2f}"],
                    "Perdida": [perdida]
                })
                df_current = pd.concat([df_current, new_data], ignore_index=True)
            
            # Write all data to Excel
            try:
                df_current.to_excel(excel_file, index=False, header=True, sheet_name='Sheet1')
                st.sidebar.success("¡Datos guardados exitosamente!")
            except Exception as e:
                st.sidebar.error(f"Error al guardar datos: {e}")

        # Delete button
        if st.button("Borrar"):
            if no_parte in no_parte_values:
                df_current = df_current[df_current["No. Parte"] != no_parte]
                try:
                    df_current.to_excel(excel_file, index=False, header=True, sheet_name='Sheet1')
                    st.sidebar.success(f"¡Articulo {no_parte} borrado exitosamente!")
                except Exception as e:
                    st.sidebar.error(f"Error al borrar el articulo: {e}")

    # Display the current data in the Excel file in the main page
    st.header("Datos Actuales")
    try:
        df_current = pd.read_excel(excel_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        df_current = pd.DataFrame()  # Initialize an empty DataFrame

    # Editable data grid in the main page
    gb = GridOptionsBuilder.from_dataframe(df_current)
    gb.configure_default_column(editable=False)  # Make all columns non-editable by default
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
            df_edited.to_excel(excel_file, index=False, header=True, sheet_name='Sheet1')
            st.success("¡Datos actualizados exitosamente!")
        except Exception as e:
            st.error(f"Error al actualizar datos: {e}")
