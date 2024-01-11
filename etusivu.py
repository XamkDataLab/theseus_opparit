import streamlit as st
import pandas as pd
from queries import *
from utils import *


color_discrete_sequence=px.colors.sequential.Viridis
st.set_page_config(layout="wide")
sns.set_theme(style='darkgrid', palette='viridis', font='serif')

df = get_theseus_data()
clean_data(df)

page = st.sidebar.selectbox(
    'Valitse sivu',
    [
        'Theseus aineisto',
        'Opinnäytetöiden lukumäärän muutos',
        '3',
        '4'
        ]
)
def plot_values():
    plot = st.selectbox(
        'Valitse kuvaaja',
        ['Opinnäytetöiden lukumäärän muutos', 
         'Opinnäytetöiden määrät oppilaitoksittain',
         'Opinnäytetöiden määrät oppilaitoksittain 2',
         'Opinnäytetöiden lukumäärän vertailu vuosittain'
         ]
    )
     
    if plot == 'Opinnäytetöiden lukumäärän muutos':
        monthly_filtered_data = filter_monthly(df)
        plot_line(monthly_filtered_data)
        
    if plot == 'Opinnäytetöiden määrät oppilaitoksittain': 
        yearly_sorted_data=filter_year_institution(df)
        selected_institutions_data=select_institution(yearly_sorted_data)
        plot_line_institutions(selected_institutions_data)

    if plot == "Opinnäytetöiden määrät oppilaitoksittain 2":
        yearly_sorted_data= filter_year_institution_sorted(df)
        plot_scatter(yearly_sorted_data)

    if plot == 'Opinnäytetöiden lukumäärän vertailu vuosittain':
        yearly_sorted_data=filter_yearly(df)
        df_yearly_filtered = year_slider(yearly_sorted_data)
        plot_bar(df_yearly_filtered)
if page == 'Theseus aineisto':
    st.header('Theseus aineiston analysointi')
    st.markdown('Taulukko opinnäytetöistä')
    st.dataframe(df)
elif page == 'Opinnäytetöiden lukumäärän muutos':
    st.header('Opinnäytetöiden lukumäärän muutos vuosina 2008-')
    plot_values()





