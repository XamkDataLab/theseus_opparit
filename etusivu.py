import streamlit as st
import pandas as pd
from queries import *
from utils import *


color_discrete_sequence=px.colors.sequential.Viridis
st.set_page_config(layout="wide")
sns.set_theme(style='darkgrid', palette='viridis', font='serif')

df = get_theseus_data()
#df2 = get_theseus_data()
clean_data(df)

page = st.sidebar.selectbox(
    'Valitse sivu',
    [
        'Theseus aineisto',
        'Opinnäytetöiden lukumäärän muutos',
        'Asiasanat'
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
    st.markdown('Tällä applikaatiolla voit visualisoida tietoja AMK-opinnäytetöistä. Kuvaajan valita tapahtuu vasemman sivun alasvetovalikosta. Aineisto on koottu Theseus.fi - ammattikorkeakoulujen opinnäytetyöt ja julkaisut verkossa -sivustolta. Tällä hetkellä aineistossa on opinnäytetyöt vuosilta 2008-06/2023. Aineisto ei sisällä YAMK-opinnäytetöitä.')
    st.markdown('Taulukko Theseus-opinnäytetöistä:')
    st.dataframe(df)
    
elif page == 'Opinnäytetöiden lukumäärän muutos':
    st.header('Opinnäytetöiden lukumäärän muutos vuosina 2008-')
    st.markdown('Tällä sivulla voit hakea tietoa opinnäyteöistä oppilaitoksittain. Kuvaajan valinta tapahtuu alasvetovalikosta. Aineisto on koottu Theseus.fi - ammattikorkeakoulujen opinnäytetyöt ja julkaisut verkossa -sivustolta. Tällä hetkellä aineistossa on opinnäytetyöt vuosilta 2008-06/2023. Aineisto ei sisällä YAMK-opinnäytetöitä.')
    plot_values()
    
#elif page == 'Asiasanat':
#        dff = filter_yearly(df2)
#        exploded_df = explode_keywords(dff)
#        cleaned_df = clean_keywords(exploded_df)
#        sorted_df = group_and_sort_keywords(cleaned_df)
#        filtered_df = filter_keywords(sorted_df)
#        selected_keywords_data = select_keywords(filtered_df)
#        plot_line_keywords(selected_keywords_data)




