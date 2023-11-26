#왼쪽에 지도 띄우고 검색한 숙소 핀 찍고 위험도별 색깔 칠하고 -현빈언니's
#오른쪽에 검색한 숙소 리스트 띄우고 -지형오빠's

#특정 숙소를 클릭하면 아래쪽에 숙소 정보 관련 정보 띄우고 주변 범죄 관련 정보도 띄우고 -서노나으니

import search
import apis.display as display
import pandas as pd
import streamlit as st
import folium


import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.display as display_api
#클릭한 숙소 id를 가져오기

col1, col2 = st.columns(2)
id = st.session_state['accommodation_id']
with st.container():
    if id:
        acc = display.accommodation_info(id)
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
            radius = 150,
            color='darkred',
            icon=folium.Icon(icon='heart',icon_color='white', color='red')
        ).add_to(m)

        col1.write(m)
        
with col2:
    accommodation_df = display_api.accommodations_simple_info(st.session_state['list_accommodation_id'],limit=5)
    with st.container():
        for idx, row in accommodation_df.iterrows():
            is_clicked = st.button(f"{row['name']} ({row['room_type']})\n\nprice: {row['price']} danger: {row['precinct_danger_normalized']+row['airbnb_danger_normalized']})",key = f"{row['id']}")
            
            if is_clicked: 
                st.session_state['accommodation_id'] = row['id']

    if st.session_state['accommodation_id']:
        id = st.session_state['accommodation_id']

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

        # st.metric('Details', acc.amenities[0])

        with st.expander('Amenities Details'):
            amm = acc.amenities[0].replace('\n','').replace('\t','').split('|')
            for a in amm:
                st.write(a)
        
        # acc1=acc.amenities.values
        # st.markdown(acc1[0])

    with tab2:
        st.subheader('Reviews')
        col1, col2 = st.columns(2)
        col1.metric('\#', int(acc.review_num[0]))
        col2.metric('Average', str(acc.review_avg[0].round(2))+' '+'⭐'*int(acc.review_avg[0].round(0)))

        col1, col2, col3 = st.columns(3)
        col1.metric('Cleanliness', acc.review_cleanliness[0].round(2))
        col2.metric('Check-in', acc.review_checkin[0].round(2))
        col3.metric('Location', acc.review_location[0].round(2))
        

    # st.header(acc.name[0]+ " ("+ acc.room_type[0]+ " , " + str(acc.price[0]) + " $)")

    # st.subheader('Host 관련 정보')

    # if acc.host_is_superhost[0] == True:
    #     st.markdown(f":first_place_medal: {acc.host_name[0]}") 
    # else:
    #     st.markdown(acc.host_name[0])


    # df3 = pd.DataFrame(acc[['host_name', 'host_is_superhost']], 
    #                 columns = ('host_name', 'host_is_superhost'))

    # st.subheader('Room 관련 정보')
    # df1 = pd.DataFrame(acc[['accommodates', 'bathrooms', 'bedrooms', 'beds','minimum_nights', 'maximum_nights']], 
    #                 columns = ['accommodates', 'bathrooms', 'bedrooms', 'beds','minimum_nights', 'maximum_nights'])
    # df1.rename(index={0:'num'}, inplace=True)
    # st.table(df1)


    # st.subheader('Amenity 관련 정보')
    # acc1=acc.amenities.values
    # st.markdown(acc1[0])


    # st.subheader('Review 관련 정보')
    # df2 = pd.DataFrame(acc[['review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location']])
    # df2 = df2.astype('float')

    # review_num = int(acc['review_num'][0])
    # review_avg = round(acc['review_avg'][0], 2)
    # review_cleanliness = round(acc['review_cleanliness'][0], 2)
    # review_checkin = round(acc['review_checkin'][0], 2)
    # review_location= round(acc['review_location'][0], 2)

    # if review_avg<=1.5:
    #     st.markdown("⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
    # elif review_avg<=2.5:
    #     st.markdown("⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
    # elif review_avg<=3.5:
    #     st.markdown("⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
    # elif review_avg<=4.5:
    #     st.markdown("⭐⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
    # else:
    #     st.markdown("⭐⭐⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")

    # st.write('Review Cleanliness: '+str(review_cleanliness)+"/5")
    # st.write('Review Check-in: '+str(review_checkin)+"/5")
    # st.write('Review Location: '+str(review_location)+"/5")

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