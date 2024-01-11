import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import seaborn as sns
import plotly.express as px
from queries import *


color_discrete_sequence=px.colors.sequential.Viridis
st.set_page_config(layout="wide")
sns.set_theme(style='darkgrid', palette='viridis', font='serif')
df = get_theseus_data

st.dataframe(df)

def clean_data(df):
    df.replace('Karelia-ammattikorkeakoulu (Pohjois-Karjalan ammattikorkeakoulu)', 'Karelia-ammattikorkeakoulu', inplace=True)
    return df


def main():
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

    if page == 'Theseus aineisto':
        st.header('Theseus aineiston analysointi')
        st.markdown('Taulukko opinnäytetöistä')
        st.dataframe(df)
    elif page == 'Opinnäytetöiden lukumäärän muutos':
        st.header('Opinnäytetöiden lukumäärän muutos vuosina 2008-')
        plot_values()
    elif page == '3':
        3()
    elif page == '4':
        4()


# --- sivu 2----
        
#--suodatus---

def filter_monthly(df):
    # Järjestelee alkuperäisen taulukon kuukausittain tai ja laskee tapahtumat/kk.
    # Palauttaa uuden taulukon jossa tapahtumat/kk ja aika indeksinä.
    dff = df.copy()
    dff['julkaisupäivä'] = pd.to_datetime(dff['julkaisupäivä'])
    dff.set_index('julkaisupäivä', inplace=True)  
    monthly_count = dff.resample('MS').count()
    monthly_count = pd.DataFrame({'aika': monthly_count.index, 'määrä': monthly_count['id']})
    return monthly_count

def filter_yearly(df):
    # Lisää taulukkoon sarakkeen jossa julkaisuvuosi.
    # Palauttaa taulukon jossa lisättynä sarake 'vuosi'.
    dff = df.copy()
    dff['julkaisupäivä'] = pd.to_datetime(dff['julkaisupäivä'])   
    dff['vuosi'] = dff['julkaisupäivä'].dt.year
    return dff

def filter_year_institution(df):
    # Ryhmittelee taulukon vuoden ja oppilaitoksen mukaan ja laskee tapahtumat/v kussakin oppilaitoksessa.
    # Palauttaa taulukon joka ryhmitelty julkaisuvuoden ja oppilaitoksen mukaan sisältäen sarakkeen jossa tapahtumat/vuosi kussakin oppilaitoksessa. 
    dff = filter_yearly(df)
    df_yearly = dff.groupby(['vuosi', 'oppilaitos']).size().reset_index(name='määrä')
    return df_yearly

def filter_year_institution_sorted(df):
    # Ryhmittelee ja järjestelee taulukon vuoden ja oppilaitoksen mukaan ja laskee tapahtumat/v kussakin oppilaitoksessa.
    # Palauttaa taulukon joka ryhmitelty julkaisuvuoden ja oppilaitoksen mukaan ja järjestelty oppilaitoksen mukaan sisältäen sarakkeen jossa tapahtumat/vuosi kussakin oppilaitoksessa. 
    df_yearly = filter_year_institution(df)
    df_yearly_sorted = df_yearly.sort_values(by='oppilaitos')
    return df_yearly_sorted


#--lomakevalinnat---

def select_institution(df_yearly):
    # Tekee usean kohteen valikon oppilaitoksista ja suodattaa tulokset visualisointia varten.
    # Palauttaa valittujen oppilaitoksien tapahtumien lukumäärät eri vuosina.

    oppilaitos_options = df_yearly['oppilaitos'].unique()
    sorted_oppilaitos_options = sorted(oppilaitos_options)
    selected_oppilaitos = st.multiselect('Valitse oppilaitos', sorted_oppilaitos_options, default=[])
    selected_institutions_data = df_yearly[df_yearly['oppilaitos'].isin(selected_oppilaitos)]
    return selected_institutions_data


def year_slider(df_values):
    # Tekee vuosilukusliderin, ryhmitelee tulokset opppilaitoksien ja vuosien mukaan sekä suodattaa tulokset visualisointia varten.
    # Palauttaa taulukon, joka ryhmitelty oppilaitoksen mukaan valittuina vuosina ja tapahtumien lukumäärän oppilaitoksittain valittuina vuosina.
    default_min_year = df_values['vuosi'].min()
    default_max_year = df_values['vuosi'].max()
    selected_years = st.slider('Valitse ajanjakso', min_value=default_min_year, max_value=default_max_year,
                value=(default_min_year, default_max_year))
    df_yearly_filtered = df_values[(df_values['vuosi'] >= selected_years[0]) & (df_values['vuosi'] <= selected_years[1])]
    df_yearly_filtered = df_yearly_filtered.groupby('oppilaitos')['vuosi'].count().reset_index(name='määrä')  
    df_yearly_filtered = df_yearly_filtered.sort_values(by='määrä', ascending=False)
    return df_yearly_filtered

#--visualisoinnit---

def marker_shapes():
    marker_shapes = {
        'Centria-ammattikorkeakoulu': 'circle',
        'Diakonia-ammattikorkeakoulu': 'circle',
        'Haaga-Helia ammattikorkeakoulu': 'circle',
        'Humanistinen ammattikorkeakoulu': 'circle',
        'Hämeen ammattikorkeakoulu': 'circle',
        'Högskolan på Åland': 'circle',
        'Jyväskylän ammattikorkeakoulu': 'circle',
        'Kaakkois-Suomen ammattikorkeakoulu': 'circle',
        'Kajaanin ammattikorkeakoulu': 'circle',
        'Karelia-ammattikorkeakoulu': 'triangle-up',
        'Kymenlaakson ammattikorkeakoulu': 'triangle-up',
        'LAB-ammattikorkeakoulu': 'triangle-up',
        'Lahden ammattikorkeakoulu': 'triangle-up',
        'Laurea-ammattikorkeakoulu': 'triangle-up',
        'Metropolia Ammattikorkeakoulu': 'triangle-up',
        'Mikkelin ammattikorkeakoulu': 'triangle-up',
        'Oulun ammattikorkeakoulu': 'triangle-up',
        'Poliisiammattikorkeakoulu': 'triangle-up',
        'Saimaan ammattikorkeakoulu': 'square',
        'Satakunnan ammattikorkeakoulu': 'square',
        'Savonia-ammattikorkeakoulu': 'square',
        'Seinäjoen ammattikorkeakoulu': 'square',
        'Tampereen ammattikorkeakoulu': 'square',
        'Turun ammattikorkeakoulu': 'square',
        'Vaasan ammattikorkeakoulu': 'square',
        'Yrkeshögskolan Arcada': 'square',
        'Yrkeshögskolan Novia': 'square',
        }  
    return marker_shapes
 
    

#---kuvaajat---

def plot_line(df_monthly):
    # Viivakuvaaja opinnäytetöiden kokonaismäärästä
    fig = px.line(
            df_monthly,
            x='aika', 
            y='määrä', 
            markers=True, 
            line_shape='linear',
            color_discrete_sequence=px.colors.sequential.Viridis,
            width=1000,   
            height=600,   
            )       
    fig.update_traces(
            line=dict(width=1.3),  
            marker=dict(size=5),   
        )
    fig.update_xaxes(tickmode='linear', tick0='2008-01-01', dtick='M12')
    fig.update_layout(
            xaxis_title='Vuosi',
            yaxis_title='Opinnäytetöiden lukumäärä',
        )
    st.plotly_chart(fig)

def plot_line_institutions(df_selected):
        # Viivakuvaaja opinnäytetöiden kokonaismäärästä oppilaitoksittain
        fig, ax = plt.subplots(figsize=(16, 9))
        sns.lineplot(data=df_selected, x='vuosi', y='määrä', hue='oppilaitos', 
                     palette="viridis", marker='o', style='oppilaitos')
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Vuosi', fontsize=14)
        plt.ylabel('Määrä', fontsize=14)
        handles, labels = ax.get_legend_handles_labels()
        plt.legend(handles, labels, title='Oppilaitos', fontsize=14, bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)

def plot_scatter(df_yearly_sorted):
    # Hajontakuvio opinnäytetöiden kokonaismäärästä oppilaitoksittain
    shapes=marker_shapes()
    fig = px.scatter(
            df_yearly_sorted,
            x='vuosi',
            y='määrä',
            color='oppilaitos',
            size='määrä',
            hover_data=['oppilaitos', 'vuosi', 'määrä'],
            width=1000,
            height=800,
            color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_layout(
            legend=dict(
            title_font=dict(size=16),  
            title_font_size=16, 
            font=dict(size=16)        
        ))
    for oppilaitos, marker_shape in shapes.items():  # <-- Change this line
        fig.update_traces(marker=dict(symbol=marker_shape), selector=dict(name=oppilaitos))
    st.plotly_chart(fig)

def plot_bar(df_yearly_filtered):
    # Vaakapylväsdiagrammi opinnäytetöiden kokonaismäärästä oppilaitoksittain
    fig = plt.figure(figsize=(15, 13))
    sns.barplot(data=df_yearly_filtered, y='oppilaitos', x='määrä', palette='viridis', orient='h')
    plt.xticks(rotation=0, fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('Opinnäytetöiden lukumäärä', fontsize=16)
    plt.ylabel('Oppilaitos', fontsize=16)
    st.pyplot(fig)


#----------


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
  
if __name__ == '__main__':
    main()
