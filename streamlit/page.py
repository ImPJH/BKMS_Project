import streamlit as st
import pandas as pd
# from urllib.request import urlopen
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.metrics.pairwise import euclidean_distances
# import plotly.express as px
# import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import json
# import requests
from streamlit_lottie import st_lottie
# import pydeck as pdk

# import geopandas as gpd

import folium
# from folium.map import Marker
# from streamlit_folium import st_folium

# from jinja2 import Template

# from folium.raster_layers import ImageOverlay

from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages

#Layout
st.set_page_config(
    page_title="BSAFE",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🫂"
    )


show_pages([
    Page("page.py","Main"),
    Page("login.py","login"),
    Page("team.py","Team"),
    Page("search.py","Search"),
    Page("listpage.py","Listpage")
])

hide_pages(['login', 'Main', 'Team','Search',"Listpage"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "list_accommodation_id" not in st.session_state:
    st.session_state['list_accommodation_id'] = None

if "accommodation_id" not in st.session_state:
    st.session_state['accommodation_id'] = None

if st.session_state.logged_in:
    col1, col2, col3 = st.sidebar.columns(3)
    if col1.button('My Page'):
        st.session_state.page = 'mypage'
        switch_page('login')
    if col2.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = 'login'
        switch_page('Main')
    
else:
    if st.sidebar.button('Login'):
        switch_page('login')


#Data Pull and Functions
st.markdown("""
<style>
.big-font {
    font-size:80px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search', 'Airbnb Info', 'Team'],
        icons=['house','search', 'list-ul', 'people'],menu_icon='airplane', default_index=0)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')

#Intro Page
if selected=="Main":
    #Header
    st.title('For Your Safe Journey')
    st.subheader('A new tool to find safe Airbnb that matches your demand.')

    st.divider()

    #Use Cases
    st.header('Airbnbs in NYC')

    airbnb = pd.read_csv('./data/airbnb_preprocessed.csv')
    attraction = pd.read_csv('./data/merged_attraction.csv')
    heatmap = pd.read_csv('./data/precinct_danger_normalized.csv')

    geo_data = './data/neighbourhoods.geojson'
    center = [40.776676, -73.971321]    # new york city 위도,경도

    m = folium.Map(location=center, zoom_start=11.5)

    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m)

    # 히트맵
    folium.Choropleth(
        geo_data=geo_data,      # .geojson 파일
        data=heatmap,           # .csv 파일
        columns=('neighbourhood', 'precinct_danger_normalized'), 
        key_on='feature.properties.neighbourhood',
        fill_color='RdBu_r',
        legend_name='danger'
    ).add_to(m)

    # attraction
    for i in attraction.index:
        folium.Marker(
            location = attraction.loc[i, ['Latitude', 'Longitude']],
            tooltip = attraction.loc[i, 'Tourist_Spot'],        # 마우스 갖다대면 나오는 문구
            popup = folium.Popup(f"{attraction.loc[i, 'Address_x']}", max_width=300, min_width=300),
            icon=folium.Icon(icon='bookmark',icon_color='lightgrey', color='cadetblue')
        ).add_to(m)

    la_guardia = [40.7900, -73.8700]
    jfk = [40.6650, -73.7821]
    newark = [40.7090, -74.1805]
    folium.Marker(location=la_guardia, 
                  tooltip='LaGuardia Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)
    folium.Marker(location=jfk, 
                  tooltip='JFK Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)
    folium.Marker(location=newark, 
                  tooltip='Newark Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)

    airbnb = airbnb.sort_values(by='airbnb_danger')
    for i in airbnb.index[:300]:
        if airbnb['room_type'][i] == 'Private room':
            folium.Circle(
                location = airbnb.loc[i, ['latitude', 'longitude']],
                tooltip = airbnb.loc[i, 'name'],        # 마우스 갖다대면 나오는 문구
                popup = folium.Popup(f"{airbnb.loc[i, 'description']}", max_width=300, min_width=300),
                radius = 30,
                color='darkgreen',
                opacity=0.65
            ).add_to(m)
        
        elif airbnb['room_type'][i] == 'Entire home/apt':
            folium.Circle(
                location = airbnb.loc[i, ['latitude', 'longitude']],
                tooltip = airbnb.loc[i, 'name'],
                popup = folium.Popup(f"{airbnb.loc[i, 'description']}", max_width=300, min_width=300),
                radius = 30,
                color='purple',
                opacity=0.65
            ).add_to(m)
        
        elif airbnb['room_type'][i] == 'Shared room':
            folium.Circle(
                location = airbnb.loc[i, ['latitude', 'longitude']],
                tooltip = airbnb.loc[i, 'name'],
                popup = folium.Popup(f"{airbnb.loc[i, 'description']}", max_width=300, min_width=300),
                radius = 30,
                color='darkblue',
                opacity=0.7
            ).add_to(m)
        
        elif airbnb['room_type'][i] == 'Hotel room':
            folium.Circle(
                location = airbnb.loc[i, ['latitude', 'longitude']],
                tooltip = airbnb.loc[i, 'name'],
                popup = folium.Popup(f"{airbnb.loc[i, 'description']}", max_width=300, min_width=300),
                radius = 30,
                color='black',
                opacity=0.5
            ).add_to(m)
    m
#Search Page
if selected=='Search':
    switch_page('Search')

if selected=='Airbnb Info':
    switch_page('Listpage')

if selected=='Team':
    switch_page('Team')
