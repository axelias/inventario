import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import altair as alt



class DataController:
    def __init__(self):
        self.data_file = "res/data.xlsx"
        self.data = None
        self.initial_inv = None
        self.current_inv = None
        self.part_numbers = None
        self.totals_summary = None
        self.weekly_data = None
        self.load_data()
        self.get_data_totals_summary()
        self.get_weekly_data()

    def load_data(self):
        #read data
        self.data = pd.read_excel(self.data_file, engine='openpyxl', parse_dates=[0, 11])

        #start indices from 1
        self.data.index = range(1, len(self.data) + 1)

        
        #set date format
        # self.data['Fecha'] = self.data['Fecha'].dt.strftime('%d/%m/%Y')

        #clean data and convert data types
        self.data["Existencia Actual (Valor)"] = self.data["Existencia Actual (Valor)"].replace(r'[\$,]', '', regex=True).astype(float)

        self.data.sort_values(by = 'Created', ascending = False, inplace = True)

        #extract part numbers
        self.part_numbers = self.data[self.data["Deleted"] != 1]["No. Parte"].dropna().unique().tolist()

    def save_data(self, row):
        # print(row)
        row = pd.DataFrame([row], columns = self.data.columns)
        self.data = pd.concat([row, self.data])
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
    
    def fitler_summary_by_part_number(self, part_number):
        result = self.totals_summary[(self.totals_summary["No. Parte"] == part_number)]
        
        if len(result) < 1:
            result = pd.DataFrame([[np.nan] * len(result.columns)], columns = result.columns)
            result['Fecha'] = [pd.to_datetime("today")]
            result['Created'] = [pd.to_datetime("today")]

            result['Descripcion'] = ['']
            result['No. Parte'] = ['']
            result['Unidad'] = ['Uno']

            result.fillna(0, inplace = True)
            result = result.convert_dtypes()
            
        else:
            result['Costo por Unidad'] = result['Costo por Unidad'].str.replace('$', '').astype(float)    
            result['Fecha'] = self.data[(self.data["No. Parte"] == part_number) & (self.data["Deleted"] != 1)].sort_values(by = 'Created', ascending = False)['Fecha'].iloc[0]
        
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
        cols = ['Total Investment', 'Existencia Actual (Valor)', 'Costo por Unidad']
        summary[cols] = summary[cols].apply(lambda x: x.apply(lambda y: f'${y}'))
        self.totals_summary = summary

    def get_initial_investment(self):
        total_initial_inv = self.totals_summary['Total Investment'].str.replace('$', '').astype(float).sum()
        return total_initial_inv
    
    def get_existing_investment(self):
        total_existing_inv = self.totals_summary['Existencia Actual (Valor)'].str.replace('$', '').astype(float).sum()
        return total_existing_inv
    
    def get_sold_value(self):
        return self.get_initial_investment() - self.get_existing_investment()
    
    def get_history(self):
        history = self.data.copy(deep = True)
        cols = ['Existencia Actual (Valor)', 'Costo por Unidad']
        history[cols] = history[cols].apply(lambda x: x.apply(lambda y: f'${y}'))
        history['Fecha'] = history['Fecha'].dt.strftime('%d/%m/%Y')
        return history
    
    def get_weekly_data(self):
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        sunday = monday + timedelta(days=6)
        self.weekly_data = self.data[(self.data['Fecha'] >= monday) & (self.data['Fecha'] <= sunday)]
        self.weekly_data['Week Day'] = self.weekly_data['Fecha'].dt.weekday
        self.weekly_data['Sale Value'] = self.weekly_data['Costo por Unidad'] * self.weekly_data['Salida (Cantidad)']
        self.weekly_data['Loss Value'] = self.weekly_data['Costo por Unidad'] * self.weekly_data['Perdida']
        self.weekly_data.sort_values(by = 'Fecha', ascending = True)
    
    def get_total_weekly_sales(self):
        total_weekly_sales = self.weekly_data['Sale Value'].sum()
        return total_weekly_sales

    def get_total_weekly_losses(self):
        total_weekly_losses = self.weekly_data['Loss Value'].sum()
        return total_weekly_losses
    
    def get_weekly_graph_data(self, col):
        weekly_sales = self.weekly_data.groupby('Week Day')[col].sum()
        days_of_week = range(7)
        weekly_sales = weekly_sales.reindex(days_of_week, fill_value=0)
        weekly_sales = weekly_sales.reset_index()
        cols = ['Day of Week', col]
        weekly_sales.columns = cols
        weekly_sales.sort_values(by = 'Day of Week', inplace = True)
        weekly_sales['Day of Week'] = weekly_sales['Day of Week'].map(lambda x: calendar.day_name[x])
        weekly_sales.reset_index(drop=True, inplace=True)
        return weekly_sales, cols


    def get_weekly_sales_graph(self, title):
        weekly_sales, cols = self.get_weekly_graph_data('Sale Value')
        return self.prepare_chart(weekly_sales, cols, title, 'green')
    
    def get_weekly_loss_graph(self, title):
        weekly_losses, cols = self.get_weekly_graph_data('Loss Value')
        return self.prepare_chart(weekly_losses, cols, title, '#d92232')


    def prepare_chart(self, data, cols, title, color):
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        chart = alt.Chart(data).mark_bar(color=color).encode(
            x=alt.X(f'{cols[0]}:O', title=f'{cols[0]}', sort = day_order),
            y=alt.Y(f'{cols[1]}:Q', title=f'{cols[1]}'),
            tooltip=cols
        )

        chart_text = alt.Chart(data).mark_text(dy=-10, color='black').encode(
            x=alt.X(f'{cols[0]}:O', sort = day_order),
            y=alt.Y(f'{cols[1]}:Q'),
            text=alt.Text(f'{cols[1]}:Q')
        )
    
        combined_chart = alt.layer(
            chart,
            chart_text
        ).properties(
            title=title
        ).configure_title(
            # fontSize=16,
            # anchor='start',
            # font='Arial'
        )
        return combined_chart