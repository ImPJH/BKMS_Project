import pandas as pd
import streamlit as st

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from util.postgresql_helper import run

# acommodation id list -> name, airbnb_danger, precinct_danger, room_type, price, latitude, longitude
def accommodations_simple_info(id_list):
    accommodation_df = pd.DataFrame()
    for i in range(len(id_list)):
        sql_accommodation = f'SELECT * FROM accommodation WHERE id = {accommodation_id[i]}'
        accommodation_info = run(sql_accommodation, 'select')

        sql_neighbourhood = f'SELECT * FROM neighbourhood WHERE neighbourhood_id = {accommodation_info.loc[0, "neighbourhood_id"]}'
        neighbourhood_info = run(sql_neighbourhood, 'select')
        neighbourhood_info = neighbourhood_info.drop('neighbourhood_id', axis=1)

        df = pd.concat([accommodation_info, neighbourhood_info], axis=1)
        df = df[['id', 'neighbourhood_id', 'neighbourhood_group', 'neighbourhood', 'precinct',
                 'name', 'latitude', 'longitude', 'room_type', 'price', 'airbnb_danger_normalized', 'precinct_danger_normalized']]
        
        accommodation_df = pd.concat([accommodation_df, df], axis=0)
    
    return accommodation_df


# accommodation id 1개 -> 숙소 관련 정보 모두 모은 dataframe을 return
def accommodation_info(id):
    sql_accommodation = f'SELECT * FROM accommodation WHERE id = {id}'
    accommodation_info = run(sql_accommodation, 'select')

    sql_host = f'SELECT * FROM host WHERE host_id = {accommodation_info.loc[0, "host_id"]}'
    host_info = run(sql_host, 'select')
    host_info = host_info.drop('host_id', axis=1)

    sql_neighbourhood = f'SELECT * FROM neighbourhood WHERE neighbourhood_id = {accommodation_info.loc[0, "neighbourhood_id"]}'
    neighbourhood_info = run(sql_neighbourhood, 'select')
    neighbourhood_info = neighbourhood_info.drop('neighbourhood_id', axis=1)

    df = pd.concat([accommodation_info, host_info, neighbourhood_info], axis=1)
    df = df[[
            'id', 'host_id', 'host_name', 'host_is_superhost', 'neighbourhood_id', 'neighbourhood_group', 'neighbourhood',
                'precinct', 'name', 'description', 'latitude', 'longitude', 'room_type', 'short_description', 
                'accommodates', 'bathrooms', 'bedrooms', 'beds', 'amenities', 'price', 'minimum_nights', 'maximum_nights',
                'review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location',
                'airbnb_danger', 'airbnb_danger_normalized', 'precinct_danger', 'precinct_danger_normalized'
            ]]

    return df


# accommodation id 1개 -> 해당 숙소 precinct의 범죄 정보 return
def crime_info(id):
    sql_accommodation = f'SELECT * FROM accommodation WHERE id = {id}'
    accommodation_info = run(sql_accommodation, 'select')




accommodation_id = [21736164, 3539618, 35430378]

st.dataframe(accommodation_info(21736164))

st.dataframe(accommodations_simple_info(accommodation_id))

