import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Define the path to the Excel file
excel_file = 'data.xlsx'

# Check if the Excel file exists; if not, create it with the appropriate headers
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=[
        "Fecha", "No. Parte", "Unidad", "Existencia Inicial", "Cantidad Entrada", 
        "Valor Entrada", "Salida Cantidad", "Valor Salida", "Existencia Final", 
        "Valor Existencia", "Perdida"
    ])
    df.to_excel(excel_file, index=False)

# Streamlit app
st.title("Inventario para Ventas")

# Load existing data to get "No. Parte" values
df_current = pd.read_excel(excel_file, engine='openpyxl')  # Explicitly specify engine here

no_parte_values = df_current["No. Parte"].dropna().unique().tolist()

# Select or input new "No. Parte" in the sidebar
st.sidebar.subheader("No. Parte")
no_parte_selection = st.sidebar.selectbox("Seleccionar No. Parte", options=["Nuevo..."] + list(map(str, no_parte_values)))
if no_parte_selection == "Nuevo...":
    no_parte = st.sidebar.text_input("No. Parte (Nuevo)", "")
else:
    no_parte = no_parte_selection

# Function to get current data for a selected part number
def get_current_data(part_number):
    if part_number in no_parte_values:
        return df_current[df_current["No. Parte"] == part_number].iloc[0]
    return None

current_data = get_current_data(no_parte)

# Input fields in the sidebar
st.sidebar.subheader("Detalles de Inventario")
fecha = st.sidebar.date_input("Fecha", pd.to_datetime(current_data["Fecha"]) if current_data is not None else pd.to_datetime("today"))
unidad = st.sidebar.selectbox("Unidad", options=["U", "P"], index=["U", "P"].index(current_data["Unidad"]) if current_data is not None else 0)
existencia_inicial = st.sidebar.number_input("Existencia Inicial", step=1, format="%d", value=int(current_data["Existencia Inicial"]) if current_data is not None else 0)
cantidad_entrada = st.sidebar.number_input("Cantidad Entrada", step=1, format="%d", value=int(current_data["Cantidad Entrada"]) if current_data is not None else 0)

# Calculate and display calculated fields
costo_por_unidad = st.sidebar.number_input("Costo por Unidad", format="%.2f", value=float(current_data["Costo por Unidad"]) if current_data is not None else 0.0)
valor_entrada = cantidad_entrada * costo_por_unidad
st.sidebar.text_input("Valor Entrada", value=f"${valor_entrada:.2f}", key="valor_entrada", disabled=True)

salida_cantidad = st.sidebar.number_input("Salida Cantidad", step=1, format="%d", value=int(current_data["Salida Cantidad"]) if current_data is not None else 0)
valor_salida = salida_cantidad * costo_por_unidad
st.sidebar.text_input("Valor Salida", value=f"${valor_salida:.2f}", key="valor_salida", disabled=True)

existencia_final = st.sidebar.number_input("Existencia Final", step=1, format="%d", value=int(current_data["Existencia Final"]) if current_data is not None else 0)
valor_existencia = existencia_final * costo_por_unidad
st.sidebar.text_input("Valor Existencia", value=f"${valor_existencia:.2f}", key="valor_existencia", disabled=True)

perdida = st.sidebar.number_input("Perdida", step=1, format="%d", value=int(current_data["Perdida"]) if current_data is not None else 0)

if st.sidebar.button("Guardar"):
    # Create a new DataFrame with the input data
    new_data = pd.DataFrame({
        "Fecha": [fecha.strftime('%d/%m/%Y')],
        "No. Parte": [no_parte],
        "Unidad": [unidad],
        "Existencia Inicial": [existencia_inicial],
        "Cantidad Entrada": [cantidad_entrada],
        "Valor Entrada": [f"${valor_entrada:.2f}"],
        "Salida Cantidad": [salida_cantidad],
        "Valor Salida": [f"${valor_salida:.2f}"],
        "Existencia Final": [existencia_final],
        "Valor Existencia": [f"${valor_existencia:.2f}"],
        "Perdida": [perdida]
    })

    # Write data to Excel, overwriting existing sheet
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        new_data.to_excel(writer, index=False, header=True, sheet_name='Sheet1')

    st.sidebar.success("¡Datos guardados exitosamente!")

# Display the current data in the Excel file in the main page
st.header("Datos Actuales")
df_current = pd.read_excel(excel_file, engine='openpyxl')

# Editable data grid in the main page
gb = GridOptionsBuilder.from_dataframe(df_current)
gb.configure_default_column(editable=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gridOptions = gb.build()

grid_response = AgGrid(
    df_current,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    allow_unsafe_jscode=True,
)

# Get edited data
df_edited = pd.DataFrame(grid_response['data'])

if st.button("Actualizar Datos"):
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        df_edited.to_excel(writer, index=False)
    st.success("¡Datos actualizados exitosamente!")
