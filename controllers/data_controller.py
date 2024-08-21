import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import altair as alt
import math



class DataController:
    def __init__(self):
        self.data_file = "res/data.xlsx"
        self.data = None
        self.initial_inv = None
        self.current_inv = None
        self.part_numbers = None
        self.totals_summary = None
        self.weekly_data = None
        self.last_week_data = None
        self.weekly_summary = None
        self.load_data()
        self.get_data_totals_summary()
        self.set_weekly_data()
        self.get_weekly_summary()

    def load_data(self):
        #read data
        self.data = pd.read_excel(self.data_file, engine='openpyxl', parse_dates=[0, 11])

        #start indices from 1
        self.data.index = range(1, len(self.data) + 1)

        
        #set date format
        # self.data['Fecha'] = self.data['Fecha'].dt.strftime('%d/%m/%Y')

        #clean data and convert data types
        self.data["Existencia Actual (Valor)"] = self.data["Existencia Actual (Valor)"].replace(r'[\$,]', '', regex=True) #.astype(float)

        self.data.sort_values(by = "Creado", ascending = False, inplace = True)

        #extract part numbers
        self.part_numbers = self.data[self.data["Borrado"] != 1]["No. Parte"].dropna().unique().tolist()

    def save_data(self, row):
        row = pd.DataFrame([row], columns = self.data.columns)
        self.data = pd.concat([row, self.data])
        self.data['Fecha'] = pd.to_datetime(self.data['Fecha'])
        # print(self.data)
        self.save_data_to_excel()
        
    def save_data_to_excel(self):
        self.data.to_excel(self.data_file, index=False)

    def remove_data(self, part_number):
        self.data.loc[self.data['No. Parte'] == part_number, "Borrado"] = 1
        self.save_data_to_excel()

    def reset_data_index(self):
        self.data.index = range(1, len(self.data) + 1)

    def filter_by_part_number(self, part_number):
        result = self.data[(self.data["No. Parte"] == part_number) & 
                           (self.data["Borrado"] != 1)].sort_values(by = "Creado", ascending = False)
        
        if len(result) < 1:
            result = pd.DataFrame([[np.nan] * len(result.columns)], columns = result.columns)
            result['Fecha'] = [pd.to_datetime("today")]
            result["Creado"] = [pd.to_datetime("today")]

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
            result["Creado"] = [pd.to_datetime("today")]

            result['Descripcion'] = ['']
            result['No. Parte'] = ['']
            result['Unidad'] = ['Uno']

            result.fillna(0, inplace = True)
            result = result.convert_dtypes()
            
        else:
            result['Costo por Unidad'] = result['Costo por Unidad'].str.replace('$', '').astype(float)    
            result['Fecha'] = self.data[(self.data["No. Parte"] == part_number) & (self.data["Borrado"] != 1)].sort_values(by = "Creado", ascending = False)['Fecha'].iloc[0]
        
        return result.iloc[0]

        
    def get_data_totals_summary(self):
        current_data = self.data[(self.data["Borrado"] != 1)]
        totals = current_data.groupby('No. Parte')[['Entrada (Cantidad)', 'Salida (Cantidad)', 'Perdida']].sum()
        totals.reset_index(inplace = True)

        finals = current_data.sort_values(by=['No. Parte', "Creado"], ascending=[True, False])
        finals = finals.drop_duplicates(subset='No. Parte', keep='first')
        finals = finals[['No. Parte', 'Descripcion', 'Unidad', 'Costo por Unidad', 'Existencia Actual', 'Existencia Actual (Valor)']]
        summary = pd.merge(finals, totals,  on='No. Parte', how='left')
        summary["Inversion Total"] = summary['Costo por Unidad'] * summary['Entrada (Cantidad)']
        summary = summary[['No. Parte', 'Descripcion', 'Unidad', 'Costo por Unidad', 'Entrada (Cantidad)', 'Salida (Cantidad)', 'Perdida', 'Existencia Actual', "Inversion Total", 'Existencia Actual (Valor)']]
        cols = ["Inversion Total", 'Existencia Actual (Valor)', 'Costo por Unidad']
        summary[cols] = summary[cols].apply(lambda x: x.apply(lambda y: f'${y}'))
        self.totals_summary = summary

    def get_initial_investment(self):
        if len(self.totals_summary) == 0:
            total_initial_inv = 0.0
        else:
            total_initial_inv = self.totals_summary["Inversion Total"].str.replace('$', '').astype(float).sum()
        return total_initial_inv
    
    def get_existing_investment(self):
        if len(self.totals_summary) == 0:
            total_existing_inv = 0.0
        else:
            total_existing_inv = self.totals_summary['Existencia Actual (Valor)'].str.replace('$', '').astype(float).sum()
        return total_existing_inv
    
    def get_sold_value(self):
        return self.get_initial_investment() - self.get_existing_investment()
    
    def get_history(self):
        history = self.data.copy(deep = True)
        cols = ['Existencia Actual (Valor)', 'Costo por Unidad']
        history[cols] = history[cols].apply(lambda x: x.apply(lambda y: f'${y}'))
        if len(history) > 0:
            history['Fecha'] = history['Fecha'].dt.strftime('%d/%m/%Y')
        return history
    
    def set_weekly_data(self):
        # Get current week data
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        sunday = monday + timedelta(days=6)

        # Get previous week data
        last_monday = monday - timedelta(days=7)
        last_sunday = sunday - timedelta(days=7)
        self.weekly_data = self.get_weekly_data(monday, sunday)
        self.last_week_data = self.get_weekly_data(last_monday, last_sunday)
        # print(self.weekly_data[['Fecha', 'Salida (Cantidad)', 'Perdida', "Valor de Venta", "Valor de Perdida"]])
        # print(self.last_week_data[['Fecha', 'Salida (Cantidad)', 'Perdida', "Valor de Venta", "Valor de Perdida"]])

    def get_weekly_data(self, monday, sunday):
        week_data = self.data[(self.data['Fecha'] >= monday) & (self.data['Fecha'] <= sunday) & (self.data["Borrado"] != 1)].copy()

        if len(week_data) > 0:
            week_data.loc[:, 'Week Day'] = week_data['Fecha'].dt.weekday
            week_data.loc[:, "Valor de Venta"] = week_data['Costo por Unidad'] * week_data['Salida (Cantidad)']
            week_data.loc[:, "Valor de Perdida"] = week_data['Costo por Unidad'] * week_data['Perdida']
            week_data.sort_values(by = 'Fecha', ascending = True)
            week_data.loc[:, 'Fecha'] = week_data['Fecha'].dt.strftime('%d/%m/%Y')
        else:
            week_data.loc[:, 'Week Day'] = []
            week_data.loc[:, "Valor de Venta"] = []
            week_data.loc[:, "Valor de Perdida"] = []
        
        # print(week_data)

        return week_data


    def get_weekly_summary(self):
        self.weekly_summary = self.weekly_data.groupby(['Fecha', 'Descripcion', 'No. Parte', 'Unidad', 'Costo por Unidad'])[['Salida (Cantidad)', 'Perdida', "Valor de Venta", "Valor de Perdida"]].sum()
        self.weekly_summary.reset_index(inplace = True)
        cols = ["Valor de Venta", "Valor de Perdida", 'Costo por Unidad']
        self.weekly_summary[cols] = self.weekly_summary[cols].apply(lambda x: x.apply(lambda y: f'${y}'))
        # if len(self.weekly_summary) > 0:
        #     self.weekly_summary['Fecha'] =  self.weekly_summary['Fecha'].dt.strftime('%d/%m/%Y')

    
    def get_total_weekly_sales(self):
        return self.get_total_weekly_data("Valor de Venta", 'Salida (Cantidad)')

    def get_total_weekly_data(self, amount_col, num_col):
        #find this week total amount and value
        weekly_amount = self.weekly_data[amount_col].sum()
        weekly_value = self.weekly_data[num_col].sum()

        #find last week total amount and value
        last_week_amount = self.last_week_data[amount_col].sum()
        last_week_value = self.last_week_data[num_col].sum()

        #find amount change percentage
        if last_week_amount != 0:
            amount_change_percent = (weekly_amount - last_week_amount) / last_week_amount * 100
        else:
            amount_change_percent = 0

        #find value change percentage
        if last_week_value != 0:
            value_change_percent = (weekly_value - last_week_value) / last_week_value * 100
        else:
            value_change_percent = 0
        return weekly_value, weekly_amount, round(amount_change_percent), round(value_change_percent)

    def get_total_weekly_losses(self):
        return self.get_total_weekly_data("Valor de Perdida", 'Perdida')
    
    def get_weekly_graph_data(self, col):
        weekly_sales = self.weekly_data.groupby('Week Day')[col].sum()
        days_of_week = range(7)
        weekly_sales = weekly_sales.reindex(days_of_week, fill_value=0)
        weekly_sales = weekly_sales.reset_index()
        cols = ['Día de la Semana', col] # day of week
        weekly_sales.columns = cols
        weekly_sales.sort_values(by = 'Día de la Semana', inplace = True)
        weekly_sales['Día de la Semana'] = weekly_sales['Día de la Semana'].map(lambda x: calendar.day_name[x])
        weekly_sales['Día de la Semana'] = weekly_sales['Día de la Semana'].map({'Monday':'Lunes', 
                                                                                 'Tuesday':'Martes', 
                                                                                 'Wednesday':'Miércoles',
                                                                                 'Thursday':'Jueves',
                                                                                 'Friday':'Viernes', 
                                                                                 'Saturday':'Sábado', 
                                                                                 'Sunday':'Domingo'})
        weekly_sales.reset_index(drop=True, inplace=True)
        return weekly_sales, cols
    
    def get_weekly_amount_graph(self, title):
        weekly_sales, cols_sales = self.get_weekly_graph_data("Valor de Venta")
        weekly_losses, cols_losses = self.get_weekly_graph_data("Valor de Perdida")
        return self.prepare_combined_chart(weekly_sales, cols_sales, weekly_losses, cols_losses, title, 'green', '#d92232')
    
    def get_weekly_value_graph(self, title):
        weekly_sales, cols_sales = self.get_weekly_graph_data('Salida (Cantidad)')
        weekly_losses, cols_losses = self.get_weekly_graph_data('Perdida')
        return self.prepare_combined_chart(weekly_sales, cols_sales, weekly_losses, cols_losses, title, 'green', '#d92232')

    def prepare_combined_chart(self, data1, cols1, data2, cols2, title, color1, color2):
        day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'] #Monday to Sunday
        chart1 = alt.Chart(data1).mark_bar(color=color1).encode(
            x=alt.X(f'{cols1[0]}:O', sort = day_order),
            y=alt.Y(f'{cols1[1]}:Q'),
            tooltip=cols1
        )

        chart_text1 = alt.Chart(data1).mark_text(dy=-10, color='black', size = 14).encode(
            x=alt.X(f'{cols1[0]}:O', 
                    sort = day_order,
                    axis=alt.Axis(
                    labelColor='black',
                    labelFontSize=14,
                    titleFontSize=16,
                    titleFontWeight='bold')),
            y=alt.Y(f'{cols1[1]}:Q', 
                    axis=alt.Axis(
                    labelColor='black',
                    labelFontSize=14,
                    titleFontSize=16,
                    titleFontWeight='bold')),
            text=alt.Text(f'{cols1[1]}:Q')
        )

        chart21 = alt.Chart(data2).mark_line(color=color2).encode(
            x=alt.X(f'{cols2[0]}:O', sort = day_order),
            y=alt.Y(f'{cols2[1]}:Q'),
            tooltip=cols2
        )

        chart22 = alt.Chart(data2).mark_point(color=color2, filled=True).encode(
            x=alt.X(f'{cols2[0]}:O', sort = day_order),
            y=alt.Y(f'{cols2[1]}:Q'),
        )

        chart_text2 = alt.Chart(data2).mark_text(dy=-10, color='#d92232', size = 14).encode(
            x=alt.X(f'{cols2[0]}:O', 
                    sort = day_order, 
                    title = f"{cols2[0]}",
                    axis=alt.Axis(
                    labelColor='black',
                    labelFontSize=14,
                    titleFontSize=16,
                    titleFontWeight='bold')),
            y=alt.Y(f'{cols2[1]}:Q', 
                    title = "Ventas vs Perdidas",
                    axis=alt.Axis(
                    labelColor='black',
                    labelFontSize=14,
                    titleFontSize=16,
                    titleFontWeight='bold')),
            text=alt.Text(f'{cols2[1]}:Q')
        )
    
        combined_chart = alt.layer(
            chart1,
            chart_text1,
            chart21,
            chart22,
            chart_text2
        ).properties(
            title=title
        ).configure_title(
            # fontSize=16,
            # anchor='start',
            # font='Arial'
        ).configure_axis(
            grid=True
        )#.configure_axisX(
         #   labelAngle=45  # Rotate x-axis labels to 45 degrees
        #)

        return combined_chart
    
    