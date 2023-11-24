import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, JsCode

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from util.postgresql_helper import run

# acommodation id list -> name, airbnb_danger, precinct_danger, room_type, price, latitude, longitude
def accommodations_simple_info(id_list,limit=None):
    accommodation_df = pd.DataFrame()
    stopper = None
    if limit: stopper = limit
    else: stopper = len(id_list)
    for i in range(stopper):
        sql_accommodation = f'SELECT * FROM accommodation WHERE id = {id_list[i]}'
        accommodation_info = run(sql_accommodation, 'select')

        sql_neighbourhood = f'SELECT * FROM neighbourhood WHERE neighbourhood_id = {accommodation_info.loc[0, "neighbourhood_id"]}'
        neighbourhood_info = run(sql_neighbourhood, 'select')
        neighbourhood_info = neighbourhood_info.drop('neighbourhood_id', axis=1)

        df = pd.concat([accommodation_info, neighbourhood_info], axis=1)
        df = df[['id', 'neighbourhood_id', 'neighbourhood_group', 'neighbourhood', 'precinct',
                 'name', 'latitude', 'longitude', 'room_type', 'price', 'airbnb_danger_normalized', 'precinct_danger_normalized']]
        
        accommodation_df = pd.concat([accommodation_df, df], axis=0,ignore_index=True)
    
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


# accommodation id 1개 + display_type(overall, date, crime_type, victim) -> 해당 숙소 precinct의 범죄 정보 return
def crime_info(id, display_type):
    # crime 테이블에서 불러오기
    sql_accommodation = f'SELECT neighbourhood_id, airbnb_danger_normalized FROM accommodation WHERE id = {id}'
    accommodation_df = run(sql_accommodation, 'select')
    neighbourhood_id = accommodation_df.loc[0, 'neighbourhood_id']
    airbnb_danger = accommodation_df.loc[0, 'airbnb_danger_normalized'] * 100000

    sql_neighbourhood = f'SELECT neighbourhood_group, neighbourhood, precinct, precinct_danger_normalized FROM neighbourhood WHERE neighbourhood_id = {neighbourhood_id}'
    neighbourhood_df = run(sql_neighbourhood, 'select')
    precinct = neighbourhood_df.loc[0, 'precinct']
    precinct_danger = neighbourhood_df.loc[0, 'precinct_danger_normalized'] * 1000
    neighbourhood_group = neighbourhood_df.loc[0, 'neighbourhood_group']
    neighbourhood = neighbourhood_df.loc[0, 'neighbourhood']

    sql_crime = f'SELECT * FROM crime WHERE precinct = {precinct}'
    crime_df = run(sql_crime, 'select')
    crime_df['date'] = pd.to_datetime(crime_df['date'])


    if display_type == 'overall':
        col1, col2, col3 = st.columns(3)
        col1.subheader('Borough')
        col1.write(neighbourhood_group)
        col2.subheader('Neighbourhood')
        col2.write(neighbourhood)
        col3.subheader('Precinct')
        col3.write(str(precinct))

        st.divider()
        st.subheader('Danger')
        col1, col2, col3 = st.columns(3)
        col1.metric('Airbnb danger', airbnb_danger.round(2))
        col1.progress(airbnb_danger/100)
        col2.metric('Neighbourhood danger', precinct_danger.round(2))
        col2.progress(precinct_danger/100)
        col3.metric('Total danger', (airbnb_danger+precinct_danger).round(2))
        col3.progress((airbnb_danger+precinct_danger)/100)

        df = pd.DataFrame([airbnb_danger, precinct_danger, airbnb_danger+precinct_danger], index=['Airbnb', 'Neighbourhood', 'Total'])
        df.reset_index(inplace=True)
        df.rename(columns={0:'danger'}, inplace=True)
        fig = px.bar(df, x='index', y='danger', color='index', color_discrete_map={'Airbnb':px.colors.qualitative.Pastel[5], 'Neighbourhood':px.colors.qualitative.Pastel[5], 'Total':px.colors.qualitative.G10[0]})
        fig.update_layout(xaxis_title = '', yaxis_title='Danger')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


    elif display_type == 'date':
        col1, col2, col3 = st.columns(3)
        col1.subheader('Borough')
        col1.write(neighbourhood_group)
        col2.subheader('Neighbourhood')
        col2.write(neighbourhood)
        col3.subheader('Precinct')
        col3.write(str(precinct))

        
        # 월별, 요일별 count
        crime_month = pd.DataFrame(crime_df['date'].dt.month.value_counts()).sort_values(by=['date']).reset_index()
        crime_month.rename(columns={'date':'month'}, inplace=True)
        crime_month['month'] = crime_month['month'].astype(str)
        crime_weekday = pd.DataFrame(crime_df['date'].dt.weekday.value_counts()).sort_values(by=['date']).reset_index()
        crime_weekday.rename(columns={'date':'weekday'}, inplace=True)
        crime_weekday['weekday'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        st.divider()

        col1, col2 = st.columns(2)
        fig_month = px.bar(crime_month, x='month', y='count', color='month', color_discrete_map={'1':px.colors.qualitative.Set3[0],
                                                                                                 '2':px.colors.qualitative.Set3[1],
                                                                                                 '3':px.colors.qualitative.Set3[2],
                                                                                                 '4':px.colors.qualitative.Set3[3],
                                                                                                 '5':px.colors.qualitative.Set3[4],
                                                                                                 '6':px.colors.qualitative.Set3[5],
                                                                                                 '7':px.colors.qualitative.Set3[6],
                                                                                                 '8':px.colors.qualitative.Set3[7],
                                                                                                 '9':px.colors.qualitative.Set3[8],
                                                                                                 '10':px.colors.qualitative.Set3[0],
                                                                                                 '11':px.colors.qualitative.Set3[10],
                                                                                                 '12':px.colors.qualitative.Set3[11]})
        fig_month.update_layout(xaxis_title='Month', yaxis_title='# Crimes')
        fig_month.update_layout(showlegend=False)
        col1.caption('Month')
        col1.plotly_chart(fig_month, use_container_width=True)
        
        fig_weekday = px.bar(crime_weekday, x='weekday', y='count', color='weekday', color_discrete_map={'Mon':px.colors.qualitative.Set3[0],
                                                                                                         'Tue':px.colors.qualitative.Set3[1],
                                                                                                         'Wed':px.colors.qualitative.Set3[2],
                                                                                                         'Thu':px.colors.qualitative.Set3[3],
                                                                                                         'Fri':px.colors.qualitative.Set3[4],
                                                                                                         'Sat':px.colors.qualitative.Set3[5],
                                                                                                         'Sun':px.colors.qualitative.Set3[6]})
        fig_weekday.update_layout(xaxis_title='Weekday', yaxis_title='# Crimes')
        fig_weekday.update_layout(showlegend=False)
        col2.caption('Weekday')
        col2.plotly_chart(fig_weekday, use_container_width=True)



    elif display_type == 'crime_type':
        col1, col2, col3 = st.columns(3)
        col1.subheader('Borough')
        col1.write(neighbourhood_group)
        col2.subheader('Neighbourhood')
        col2.write(neighbourhood)
        col3.subheader('Precinct')
        col3.write(str(precinct))

        # 범죄유형별 count
        crime_type = pd.DataFrame(crime_df['crime_type'].value_counts()).reset_index()
        crime_type_all = ['ROBBERY', 'RAPE', 'GRAND LARCENY', 'THEFT-FRAUD',
                        'GRAND LARCENY OF MOTOR VEHICLE', 'DANGEROUS WEAPONS', 'BURGLARY',
                        'SEX CRIMES', 'FELONY ASSAULT', 'DANGEROUS DRUGS',
                        'MURDER & NON-NEGL. MANSLAUGHTER',
                        'HOMICIDE-NEGLIGENT,UNCLASSIFIE', 'ARSON',
                        'PROSTITUTION & RELATED OFFENSES', 'KIDNAPPING & RELATED OFFENSES',
                        'INTOXICATED/IMPAIRED DRIVING', 'FELONY SEX CRIMES', 'KIDNAPPING']
        crime_type_add = list(set(crime_type_all) - set(list(crime_type['crime_type'].unique())))
        crime_count_add = [0] * len(crime_type_add)
        crime_type_add = pd.DataFrame(crime_type_add, columns=['crime_type'])
        crime_count_add = pd.DataFrame(crime_count_add, columns=['count'])
        crime_add = pd.concat([crime_type_add, crime_count_add], axis=1)
        crime_type = pd.concat([crime_type, crime_add], axis=0).reset_index(drop=True)

        st.divider()
        st.subheader('# Crimes by Crime Type')

        for i in range(5):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(crime_type.loc[i*4+0, 'crime_type'], crime_type.loc[i*4+0, 'count'])
            col2.metric(crime_type.loc[i*4+1, 'crime_type'], crime_type.loc[i*4+1, 'count'])
            if i == 4:
                break
            col3.metric(crime_type.loc[i*4+2, 'crime_type'], crime_type.loc[i*4+2, 'count'])
            col4.metric(crime_type.loc[i*4+3, 'crime_type'], crime_type.loc[i*4+3, 'count'])
            st.divider()
        


    elif display_type == 'victim':
        col1, col2, col3 = st.columns(3)
        col1.subheader('Borough')
        col1.write(neighbourhood_group)
        col2.subheader('Neighbourhood')
        col2.write(neighbourhood)
        col3.subheader('Precinct')
        col3.write(str(precinct))

        # 피해자 성별, 나이, 인종
        crime_sex = pd.DataFrame(crime_df['vic_sex'].value_counts())
        cnt = 0
        if 'E' in crime_sex.index:
            cnt += crime_sex.loc['E']
        if 'D' in crime_sex.index:
            cnt += crime_sex.loc['D']
        if 'L' in crime_sex.index:
            cnt += crime_sex.loc['L']
        dict = {'count':cnt['count']}
        sex_unknown = pd.DataFrame(dict, index=['UNKNOWN'])
        crime_sex = pd.concat([crime_sex, sex_unknown])
        crime_sex.drop('E', inplace=True)
        crime_sex.drop('D', inplace=True)
        crime_sex.drop('L', inplace=True)
        crime_sex.reset_index(inplace=True)
        crime_sex.rename(columns={'index':'vic_sex'}, inplace=True)
        crime_age = pd.DataFrame(crime_df['vic_age_group'].value_counts()).reset_index()
        crime_race = pd.DataFrame(crime_df['vic_race'].value_counts()).reset_index()

        st.divider()

        col1, col2, col3 = st.columns(3)

        fig_sex = px.pie(crime_sex, values='count', names='vic_sex', color='vic_sex', color_discrete_map={'F':px.colors.qualitative.Pastel1[0], 'M':px.colors.qualitative.Pastel1[1], 'UNKNOWN':px.colors.qualitative.Pastel1[2]})
        fig_sex.update_traces(textposition='inside', textinfo='percent+label')
        fig_sex.update_layout(showlegend=False)
        # fig_sex.update_layout(legend={'title':'Sex'}, legend_yanchor='bottom', legend_y=0.01, legend_xanchor='left', legend_x=0.01, legend_orientation='v', legend_entrywidth=200)
        col1.caption('Victim Sex')
        col1.plotly_chart(fig_sex, use_container_width=True)
        
        fig_age = px.pie(crime_age, values='count', names='vic_age_group', color='vic_age_group', color_discrete_sequence=px.colors.qualitative.Set2)
        fig_age.update_traces(textposition='inside', textinfo='percent+label')
        fig_age.update_layout(showlegend=False)
        # fig_age.update_layout(legend={'title':'Age Group'}, legend_yanchor='bottom', legend_y=0.01, legend_xanchor='left', legend_x=0.01, legend_orientation='v', legend_entrywidth=200)
        col2.caption('Victim Age Group')
        col2.plotly_chart(fig_age, use_container_width=True)
        
        fig_race = px.pie(crime_race, values='count', names='vic_race', color='vic_race', color_discrete_sequence=px.colors.qualitative.Set3)
        fig_race.update_traces(textposition='inside', textinfo='percent+label')
        fig_race.update_layout(showlegend=False)
        # fig_race.update_layout(legend={'title':'Race'}, legend_yanchor='bottom', legend_y=0.01, legend_xanchor='left', legend_x=0.01, legend_orientation='v', legend_entrywidth=200)
        col3.caption('Victim Race')
        col3.plotly_chart(fig_race, use_container_width=True)





# crime_info(3539618, 'overall')
# crime_info(3539618, 'date')
# crime_info(3539618, 'crime_type')
# crime_info(3539618, 'victim')
