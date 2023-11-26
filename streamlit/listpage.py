import json
import search
import apis.display as display
import pandas as pd
import streamlit as st
import folium
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.display as display_api
#클릭한 숙소 id를 가져오기



def make_map(id):
    acc = display_api.accommodation_info(id)
    attraction = pd.read_csv('./data/merged_attraction.csv')
    heatmap = pd.read_csv('./data/precinct_danger_normalized.csv')

    geo_data = './data/neighbourhoods.geojson'
    latitude, longitude = acc['latitude'][0], acc['longitude'][0]
    center = [latitude, longitude]    # 숙소 위도 경도

    m = folium.Map(location=center, zoom_start=12)

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

    folium.Marker(
        location = [acc['latitude'][0], acc['longitude'][0]],
        tooltip = acc['name'][0],        # 마우스 갖다대면 나오는 문구
        popup = folium.Popup(f"{acc['description'][0]}", max_width=300, min_width=300),
        icon=folium.Icon(icon='heart',icon_color='white', color='red')
    ).add_to(m)

    return m


show_pages([
    Page("page.py","Main"),
    Page("login.py","login"),
    Page("team.py","Team"),
    Page("search.py","Search"),
    Page("listpage.py","Listpage")
])

hide_pages(['login', 'Main', 'Team','Search','Listpage'])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if st.sidebar.button('logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        switch_page('Listpage')
else:
    if st.sidebar.button('login'):
        switch_page('login')



@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search', 'Airbnb Info', 'Team'],
        icons=['house','search', 'list-ul', 'people'],menu_icon='airplane', default_index=2)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')

if selected == "Main":
    switch_page('Main')

if selected == "Search":
    switch_page("Search")


if selected == 'Airbnb Info':
    if st.session_state['list_accommodation_id'] is not None:
        col1, col2 = st.columns(2)
        id = st.session_state['accommodation_id']


        with col2:
            accommodation_df = display_api.accommodations_simple_info(st.session_state['list_accommodation_id'],limit=5)
            with st.container():
                for idx, row in accommodation_df.iterrows():
                    is_clicked = st.button(f"[danger: {round(row['precinct_danger_normalized']*1000+row['airbnb_danger_normalized']*100000, 2)}] {row['name']}\n\n$ {row['price']} / {row['room_type']}", key = f"{row['id']}")
                    
                    if is_clicked: 
                        st.session_state['accommodation_id'] = row['id']

            if st.session_state['accommodation_id']:
                id = st.session_state['accommodation_id']

        with st.container():
            if id:
                m = make_map(id)
                col1.write(m)

            else:
                # id=None(지역검색인 경우) -> 첫번째 숙소로 지도 그리기
                m = make_map(st.session_state['list_accommodation_id'][0])
                col1.write(m)


        if id:
            acc = display.accommodation_info(id)
            #'name' ('room_type', 'price')
            #host 관련 정보 : 'host_name', 'host_is_superhost'
            #room 관련 정보 : 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'amenities', 'minimum_nights', 'maximum_nights'
            #review 관련 정보 : 'review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location'
            
            st.divider()
            st.title(acc.name[0])

            col1, col2, col3 = st.columns(3)
            col1.metric('Price', str(acc.price[0]) + ' $')
            col2.metric('Room Type', acc.room_type[0])
            if acc.host_is_superhost[0] == True:
                col3.metric('Host', f"{acc.host_name[0]} ✅")
            else:
                col3.metric('Host', acc.host_name[0])

            tab1, tab2 = st.tabs(['Room Information', 'Reviews'])
            with tab1:
                st.subheader('Room Information')
                col1, col2, col3 = st.columns(3)
                col1.metric('Accommodates', acc.accommodates[0])
                col2.metric('Min Nights', acc.minimum_nights[0])
                col3.metric('Max Nights', acc.maximum_nights[0])

                st.divider()

                st.subheader('Amenities')
                col1, col2, col3 = st.columns(3)
                col1.metric('Bathrooms', acc.bathrooms[0])
                col2.metric('Bedrooms', acc.bedrooms[0])
                col3.metric('Beds', acc.beds[0])


                with st.expander('Amenities Details'):
                    amm = acc.amenities[0].replace('\n','').replace('\t','').split('|')
                    for a in amm:
                        st.write(a)

            with tab2:
                st.subheader('Reviews')
                col1, col2 = st.columns(2)
                col1.metric('\#', int(acc.review_num[0]))
                col2.metric('Average', str(acc.review_avg[0].round(2))+' '+'⭐'*int(acc.review_avg[0].round(0)))

                col1, col2, col3 = st.columns(3)
                col1.metric('Cleanliness', acc.review_cleanliness[0].round(2))
                col2.metric('Check-in', acc.review_checkin[0].round(2))
                col3.metric('Location', acc.review_location[0].round(2))
                

            st.divider()

            st.title('Crime Information')

            neighbourhood_group, neighbourhood, precinct = display.neighbourhood_info(id)
            col1, col2, col3 = st.columns(3)
            col1.metric('Borough', neighbourhood_group)
            col2.metric('Neighbourhood', neighbourhood)
            col3.metric('Precinct', precinct)

            st.divider()

            tab1, tab2, tab3, tab4 = st.tabs(['Overall', 'Date', 'Crime Type', 'Victim'])
            with tab1:
                display.crime_info(id, 'overall')
            with tab2:
                display.crime_info(id, 'date')
            with tab3:
                display.crime_info(id, 'crime_type')
            with tab4:
                display.crime_info(id, 'victim')

    else:
        switch_page('Search')

if selected=='Team':
    switch_page('Team')
