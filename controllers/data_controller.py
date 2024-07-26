import pandas as pd
import numpy as np

class DataController:
    def __init__(self):
        self.data_file = "res/data.xlsx"
        self.data = None
        self.initial_inv = None
        self.current_inv = None
        self.part_numbers = None
        self.totals_summary = None
        self.load_data()
        self.get_data_totals_summary()

    def load_data(self):
        #read data
        self.data = pd.read_excel(self.data_file, engine='openpyxl', parse_dates=[0, 11])

        #start indices from 1
        self.data.index = range(1, len(self.data) + 1)

        
        #set date format
        # self.data['Fecha'] = self.data['Fecha'].dt.strftime('%d/%m/%Y')

        #clean data and convert data types
        self.data["Existencia Actual (Valor)"] = self.data["Existencia Actual (Valor)"].replace(r'[\$,]', '', regex=True).astype(float)

        #extract part numbers
        self.part_numbers = self.data[self.data["Deleted"] != 1]["No. Parte"].dropna().unique().tolist()

        #-----something here-----

    def save_data(self, row):
        # print(row)
        row = pd.DataFrame([row], columns = self.data.columns)
        self.data = pd.concat([self.data, row])
        # print(self.data)
        self.save_data_to_excel()
        
    def save_data_to_excel(self):
        self.data.to_excel(self.data_file, index=False)

    def remove_data(self, part_number):
        self.data.loc[self.data['No. Parte'] == part_number, 'Deleted'] = 1
        self.save_data_to_excel()

    def reset_data_index(self):
        self.data.index = range(1, len(self.data) + 1)

    def filter_by_part_number(self, part_number):
        result = self.data[(self.data["No. Parte"] == part_number) & 
                           (self.data["Deleted"] != 1)].sort_values(by = 'Created', ascending = False)
        
        if len(result) < 1:
            result = pd.DataFrame([[np.nan] * len(result.columns)], columns = result.columns)
            result['Fecha'] = [pd.to_datetime("today")]
            result['Created'] = [pd.to_datetime("today")]

            result['Descripcion'] = ['']
            result['No. Parte'] = ['']
            result['Unidad'] = ['Uno']

            result.fillna(0, inplace = True)
        return result.iloc[0]
        
    def get_data_totals_summary(self):
        current_data = self.data[(self.data["Deleted"] != 1)]
        totals = current_data.groupby('No. Parte')[['Entrada (Cantidad)', 'Salida (Cantidad)', 'Perdida']].sum()
        totals.reset_index(inplace = True)

        finals = current_data.sort_values(by=['No. Parte', 'Created'], ascending=[True, False])
        finals = finals.drop_duplicates(subset='No. Parte', keep='first')
        finals = finals[['No. Parte', 'Descripcion', 'Unidad', 'Costo por Unidad', 'Existencia Actual', 'Existencia Actual (Valor)']]
        summary = pd.merge(finals, totals,  on='No. Parte', how='left')
        summary['Total Investment'] = summary['Costo por Unidad'] * summary['Entrada (Cantidad)']
        summary = summary[['No. Parte', 'Descripcion', 'Unidad', 'Costo por Unidad', 'Entrada (Cantidad)', 'Salida (Cantidad)', 'Perdida', 'Existencia Actual', 'Total Investment', 'Existencia Actual (Valor)']]
        summary[['Total Investment', 'Existencia Actual (Valor)']] = summary[['Total Investment', 'Existencia Actual (Valor)']].apply(lambda x: x.apply(lambda y: f'${y}'))
        self.totals_summary = summary

    def get_initial_investment(self):
        total_initial_inv = self.totals_summary['Total Investment'].str.replace('$', '').astype(float).sum()
        return total_initial_inv
    
    def get_existing_investment(self):
        total_existing_inv = self.totals_summary['Existencia Actual (Valor)'].str.replace('$', '').astype(float).sum()
        return total_existing_inv
    
    def get_sold_value(self):
        return self.get_initial_investment() - self.get_existing_investment()

