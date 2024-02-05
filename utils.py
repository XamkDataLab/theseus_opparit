import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import seaborn as sns
import plotly.express as px

def clean_data(df):
    df.replace('Karelia-ammattikorkeakoulu (Pohjois-Karjalan ammattikorkeakoulu)', 'Karelia-ammattikorkeakoulu', inplace=True)
    return df
    
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

def filter_yearly_keywords(df):
    # Lisää taulukkoon sarakkeen jossa julkaisuvuosi.
    # Palauttaa taulukon jossa lisättynä sarake 'vuosi'.
    try:
        dff = df.copy()
        dff['julkaisupäivä'] = pd.to_datetime(dff['julkaisupäivä'])
        dff['vuosi'] = dff['julkaisupäivä'].dt.year
        return dff
    except pd.errors.OutOfBoundsDatetime as e:
        print(f"Error converting 'julkaisupäivä' to datetime: {e}")

def explode_keywords(dff):
    # Muuttaa asiasanat sarakkeen listaksi ja hajoittaa sen yksittäisiksi sanoiksi
    # Palauttaa taulukon, jossa jokainen asiasana on omalla rivillään
    try:
        dff['asiasanat'] = dff['asiasanat'].apply(lambda x: [] if pd.isna(x) or not x else [asiasana.strip() for asiasana in x.strip("[]").replace("'", "").replace(";", ",").split(",")])
        exploded_df = dff.explode('asiasanat')
        exploded_df.dropna(subset=['asiasanat'], inplace=True)
        return exploded_df
    except pd.errors.SomeSpecificError as e:
        print(f"Explode keywords error: {e}")

def clean_keywords(exploded_df):
    # Muuttaa sanat pienaakkosiksi, poistaa tyhjät rivit, poistaa sanojen aluista ja lopuista ylimääräiset merkit.
    # Palauttaa siivotun taulukon.
    exploded_df['asiasanat'] = exploded_df['asiasanat'].str.lower()
    exploded_df = exploded_df[exploded_df['asiasanat'] != '-'].copy() 
    exploded_df = exploded_df[exploded_df['asiasanat'] != ' '].copy() 
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[5:] if x and (x[:5] == r'\u200') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[6:] if x and (x[:6] == r'\ufeff') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[6:] if x and (x[:6] == r'\u202f') else x)

    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[2:] if x and (x[:2] == '/-') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[2:] if x and (x[:2] == '; ') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[2:] if x and (x[:2] == ': ') else x)

    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[1:-1] if x and (len(x) >= 2 and x[0] == '"' and x[-1] == '"') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[1:-1] if x and (len(x) >= 2 and x[0] == '”' and x[-1] == '”') else x)
    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[1:-1] if x and (len(x) >= 2 and x[0] == '(' and x[-1] == ')') else x)

    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[1:] if x and (x[0] == '-' or 
                                                                                          x[0] == ':' or 
                                                                                          x[0] == '"' or 
                                                                                          x[0] == '´' or 
                                                                                          x[0] == ' ' or 
                                                                                          x[0] == '”'
                                                                                         ) else x)

    exploded_df['asiasanat'] = exploded_df['asiasanat'].apply(lambda x: x[:-1] if x and (x[-1] == '.' or 
                                                                                          x[-1] == '-' or 
                                                                                          x[-1] == '!' or 
                                                                                          x[-1] == ';' or 
                                                                                          x[-1] == '®' or 
                                                                                          x[-1] == '™' or
                                                                                           x[-1] == ' '
                                                                                          ) else x)


    cleaned_df=exploded_df.copy()
    return cleaned_df
    
def group_and_sort_keywords(cleaned_df):
    # Ryhmittelee ja järjestelee taulukon vuoden ja asiasanan mukaan ja laskee avainsanojen määrän vuodessa.
    # Palauttaa taulukon joka ryhmitelty julkaisuvuoden ja asiasanan mukaan ja järjestelty aakkosjärjestykseen avaisanan mukaan. 
    try:
        grouped_df = cleaned_df.groupby(['vuosi', 'asiasanat']).size().reset_index(name='määrä')
        sorted_df = grouped_df.sort_values(by=['vuosi', 'asiasanat']).reset_index(drop=True)
        return sorted_df
    except Exception as e:
        print(f"Grouping and sorting keywords error: {e}")

def filter_keywords(sorted_df):
    # Laskee jokaisen asiasanan kokonaismäärän. 
    # Poistaa alkuperäisestä taulukosta esiitymät joiden kokonaismäärä on alle 5.
    # Palauttaa suodatetun taulukon, jossa jokaista avainsanaa on vähintää 5 kpl yhteensä.
    try:    
        grouped_filter_df = sorted_df.groupby('asiasanat')['määrä'].sum().reset_index()
        filtered_asiasanat = grouped_filter_df[grouped_filter_df['määrä'] >= 5]['asiasanat']
        filtered_df = sorted_df[sorted_df['asiasanat'].isin(filtered_asiasanat)]
        
        return filtered_df
    except Exception as e:
        print(f"Filtering and grouping keywords error: {e}")


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

def select_keywords(filtered_df):
    # Tekee usean kohteen valikon avainsanoista ja suodattaa tulokset visualisointia varten.
    # Palauttaa valittujen avainsanojen tapahtumien lukumäärät eri vuosina.
    try:
        keywords_options = filtered_df['asiasanat'].unique()
        sorted_keywords_options = sorted(keywords_options)
        if sorted_keywords_options and sorted_keywords_options[0] == '':
            sorted_keywords_options.pop(0)
        selected_keywords = st.multiselect('Valitse asiasana', sorted_keywords_options, default=[])
        selected_keywords_data = filtered_df[filtered_df['asiasanat'].isin(selected_keywords)]
        return selected_keywords_data
    except Exception as e:
        print(f"Processing selected keywords error: {e}")

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


def plot_line_keywords(df_selected):
    # Viivakuvaaja avainsanojen kokonaismäärästä oppilaitoksittain
    try:
        fig, ax = plt.subplots(figsize=(16, 9))

        if df_selected.empty:
            st.markdown('Tällä sivulla voit hakea AMK-opinnäytetöissä käytettyjä asiasanoja. Voit valita yhden tai useamman asiasanan samanaikaisesti. Asiasanan valinta tapahtuu alasvetovalikosta tai vaihtoehtoisesti voit kirjoittaa asiasanan alun alasvetovalikon kohtaan Choose an option. Applikaatio näyttää vain ne asiasanat, joiden kokonaismäärä on kaikkina vuosina yhteensä yli 5.')
            st.markdown('Aineisto on koottu Theseus.fi - ammattikorkeakoulujen opinnäytetyöt ja julkaisut verkossa -sivustolta. Tällä hetkellä aineistossa on opinnäytetyöt vuosilta 2008-06/2023. Aineisto ei sisällä YAMK-opinnäytetöitä.')
            return 

        sns.lineplot(data=df_selected, x='vuosi', y='määrä', hue='asiasanat', 
                     palette='tab20', marker='o', markersize=8, style='asiasanat', dashes=False)

        min_year = df_selected['vuosi'].min() - 1
        max_year = df_selected['vuosi'].max() + 1
        all_years = np.arange(min_year, max_year)
        all_years_df = pd.DataFrame({'vuosi': all_years})
        df_selected = pd.merge(all_years_df, df_selected, on='vuosi', how='left')
        df_selected = df_selected[df_selected['vuosi'] != 0]

        x_ticks = df_selected['vuosi'].unique()
        plt.xticks(x_ticks, fontsize=14)
        plt.xlabel('Vuosi', fontsize=14)
        plt.ylabel('Asiasanojen lukumäärä', fontsize=14)
        handles, labels = ax.get_legend_handles_labels()
        plt.legend(handles, labels, title='Asiasana', fontsize=14, bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)
    
    except Exception as e:
        print(f"Plotting line keywords error: {e}")
