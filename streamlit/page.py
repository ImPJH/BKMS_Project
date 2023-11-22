import streamlit as st
import pandas as pd
from urllib.request import urlopen
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import json
import requests
from streamlit_lottie import st_lottie
import pydeck as pdk
import snowflake.connector

import geopandas as gpd

import folium
from folium.map import Marker
from streamlit_folium import st_folium

from jinja2 import Template

from folium.raster_layers import ImageOverlay
from imageio import imread


#Layout
st.set_page_config(
    page_title="BSAFE",
    layout="wide",
    initial_sidebar_state="expanded")

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

@st.cache_data
def pull_clean():
    master_zip=pd.read_csv('./reference/MASTER_ZIP.csv',dtype={'ZCTA5': str})
    master_city=pd.read_csv('./reference/MASTER_CITY.csv',dtype={'ZCTA5': str})
    return master_zip, master_city



#Options Menu
with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search','Team'], 
        icons=['play-btn','search','info-circle'],menu_icon='intersect', default_index=0)
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

    # folium으로 500개 -> 안 뜸 ... 가장 문제
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
if selected=="Search":

    st.subheader('Select Location')

    master_zip,master_city=pull_clean()
    master_zip.columns = master_zip.columns.str.upper()
    master_zip = master_zip.rename(columns={'ZCTA5': 'ZIP'})
    master_zip['ZIP'] = master_zip['ZIP'].astype(str).str.zfill(5)
    master_city.columns = master_city.columns.str.upper()

    loc_select=st.radio('Type',['Zip','City'],horizontal=True, label_visibility="collapsed")

    if loc_select=='City':
        city_select=st.selectbox(label='city',options=['City']+list(master_city['CITYSTATE'].unique()),label_visibility='collapsed')
        st.caption('Note: City is aggregated to the USPS designation which may include additional nearby cities/towns/municipalities')
        zip_select='Zip'
    if loc_select=='Zip':
        zip_select = st.selectbox(label='zip',options=['Zip']+list(master_zip['ZIP'].unique()),label_visibility='collapsed')

    with st.expander('Advanced Settings'):

        st.subheader('Filter Results')
        col1,col2=st.columns(2)
        states=sorted(list(master_zip['STATE_LONG'].astype(str).unique()))
        state_select=col1.multiselect('Filter Results by State(s)',states)
        count_select=col2.number_input(label='How many similar locations returned? (5-25)',min_value=5,max_value=25,value=10,step=5)
        st.subheader('Data Category Importance')
        st.caption('Lower values = lower importance, higher values = higher importnace, default = 1.0')
        people_select=st.slider(label='People',min_value=0.1, max_value=2.0, step=0.1, value=1.0)
        home_select=st.slider(label='Home',min_value=0.1, max_value=2.0, step=0.1, value=1.0)
        work_select=st.slider(label='Work',min_value=0.1, max_value=2.0, step=0.1, value=1.0)
        environment_select=st.slider(label='Environment',min_value=0.1, max_value=2.0, step=0.1, value=1.0)

    filt_master_zip=master_zip
    filt_master_city=master_city
    if len(state_select)>0:
        filt_master_zip=master_zip[master_zip['STATE_LONG'].isin(state_select)]
        filt_master_city=master_city[master_city['STATE_LONG'].isin(state_select)]

    #Benchmark
    if loc_select=='City':
        if city_select !='City':
            selected_record = master_city[master_city['CITYSTATE']==city_select].reset_index()
            selected_city=selected_record['CITYSTATE'][0]
            #selected_county=selected_record['County Title'][0]
            #Columns for scaling
            PeopleCols_sc=['MED_AGE_SC','PCT_UNDER_18_SC','MED_HH_INC_SC', 'PCT_POVERTY_SC','PCT_BACH_MORE_SC']
            HomeCols_sc=['HH_SIZE_SC','PCT_OWN_SC','MED_HOME_SC','PCT_UNIT1_SC','PCT_UNIT24_SC']
            WorkCols_sc=['MEAN_COMMUTE_SC','PCT_WC_SC','PCT_WORKING_SC','PCT_SERVICE_SC','PCT_BC_SC']
            EnvironmentCols_sc=['PCT_WATER_SC','ENV_INDEX_SC','PCT_TOPARK_ONEMILE_SC','POP_DENSITY_SC','METRO_INDEX_SC']
            
            # Calculate the euclidian distance between the selected record and the rest of the dataset
            People_dist             = euclidean_distances(filt_master_city.loc[:, PeopleCols_sc], selected_record[PeopleCols_sc].values.reshape(1, -1))
            Home_dist               = euclidean_distances(filt_master_city.loc[:, HomeCols_sc], selected_record[HomeCols_sc].values.reshape(1, -1))
            Work_dist               = euclidean_distances(filt_master_city.loc[:, WorkCols_sc], selected_record[WorkCols_sc].values.reshape(1, -1))
            Environment_dist        = euclidean_distances(filt_master_city.loc[:, EnvironmentCols_sc], selected_record[EnvironmentCols_sc].values.reshape(1, -1))

            # Create a new dataframe with the similarity scores and the corresponding index of each record
            df_similarity = pd.DataFrame({'PEOPLE_SIM': People_dist [:, 0],'HOME_SIM': Home_dist [:, 0],'WORK_SIM': Work_dist [:, 0],'ENV_SIM': Environment_dist [:, 0], 'index': filt_master_city.index})

            #df_similarity['OVERALL_SIM']=df_similarity['PEOPLE_SIM','HOME_SIM','WORK_SIM','ENV_SIM'].mean(axis=1)
            weights=[people_select,home_select,work_select,environment_select]
            # Multiply column values with weights
            df_weighted = df_similarity.loc[:, ['PEOPLE_SIM', 'HOME_SIM', 'WORK_SIM','ENV_SIM']].mul(weights)
            df_similarity['OVERALL_W']=df_weighted.sum(axis=1)/sum(weights)

            people_max=df_similarity['PEOPLE_SIM'].max()
            home_max=df_similarity['HOME_SIM'].max()
            work_max=df_similarity['WORK_SIM'].max()
            env_max=df_similarity['ENV_SIM'].max()
            overall_max=df_similarity['OVERALL_W'].max()

            df_similarity['PEOPLE']  = 100 - (100 * df_similarity['PEOPLE_SIM'] / people_max)
            df_similarity['HOME']    = 100 - (100 * df_similarity['HOME_SIM'] / home_max)
            df_similarity['WORK']    = 100 - (100 * df_similarity['WORK_SIM'] / work_max)
            df_similarity['ENVIRONMENT']     = 100 - (100 * df_similarity['ENV_SIM'] / env_max)
            df_similarity['OVERALL'] = 100 - (100 * df_similarity['OVERALL_W'] / overall_max)

            # Sort the dataframe by the similarity scores in descending order and select the top 10 most similar records
            df_similarity = df_similarity.sort_values(by='OVERALL_W', ascending=True).head(count_select+1)

            # Merge the original dataframe with the similarity dataframe to display the top 10 most similar records
            df_top10 = pd.merge(df_similarity, filt_master_city, left_on='index', right_index=True).reset_index(drop=True)
            df_top10=df_top10.loc[1:count_select]
            df_top10['Rank']=list(range(1,count_select+1))
            df_top10['Ranking']=df_top10['Rank'].astype(str)+'- '+df_top10['CITYSTATE']
            df_top10['LAT_R']=selected_record['LAT'][0]
            df_top10['LON_R']=selected_record['LON'][0]
            df_top10['SAVE']=False
            df_top10['NOTES']=''

            st.header('Top '+'{}'.format(count_select)+' Most Similar Locations')
            #st.write('You selected zip code '+zip_select+' from '+selected_record['County Title'][0])
            # CSS to inject contained in a string
            hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            tab1,tab2=st.tabs(['Map','Data'])
            with tab2:
                with st.expander('Expand for Table Info'):
                    st.markdown(
                    """
                    - The values for OVERALL, PEOPLE, HOME, WORK, and ENVIRONMENT are scaled similarity scores for the respective categories with values of 0-100, where 100 represents a perfect match.
                    - Locations are ranked by their OVERALL score, which is a weighted average of the individual category scores.
                    - Save your research by checking locations in the SAVE column which will be added to csv for download.
                    """
                    )
                @st.cache_data
                def convert_df(df):
                    return df.to_csv().encode('utf-8')
                cols=['Rank','CITYSTATE','OVERALL','PEOPLE','HOME','WORK','ENVIRONMENT']
                df=df_top10[cols+['SAVE','NOTES']]
                df=df.set_index('Rank')
                edited_df=st.experimental_data_editor(df)
                save=edited_df[edited_df['SAVE']==True]
                save=save.reset_index()
                csv = convert_df(save[cols+['SAVE','NOTES']])
                st.download_button(label="Download Selections as CSV",data=csv,file_name='SIMILO_SAVED.csv',mime='text/csv',)
            with tab1:
                latcenter=df_top10['LAT'].mean()
                loncenter=df_top10['LON'].mean()
                #map token for additional map layers
                token = "pk.eyJ1Ijoia3NvZGVyaG9sbTIyIiwiYSI6ImNsZjI2djJkOTBmazU0NHBqdzBvdjR2dzYifQ.9GkSN9FUYa86xldpQvCvxA" # you will need your own token
                #mapbox://styles/mapbox/streets-v12
                fig1 = px.scatter_mapbox(df_top10, lat='LAT',lon='LON',center=go.layout.mapbox.Center(lat=latcenter,lon=loncenter),
                                     color="Rank", color_continuous_scale=px.colors.sequential.ice, hover_name='CITYSTATE', hover_data=['Rank'],zoom=3,)
                fig1.update_traces(marker={'size': 15})
                fig1.update_layout(mapbox_style="mapbox://styles/mapbox/satellite-streets-v12",
                               mapbox_accesstoken=token)
                fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig1,use_container_width=True)

            st.divider()

            st.header('Location Deep Dive')
            rank_select=st.selectbox('Select from rankings above',list(df_top10['Ranking']))
            if rank_select:
                compare_record=df_top10[df_top10['Ranking']==rank_select].reset_index(drop=True)
                compare_city=compare_record['CITYSTATE'][0]
                #compare_county=compare_record['County Title'][0]
                compare_state=compare_record['STATE_SHORT'][0].lower()
                #st.write(selected_zip+' in '+selected_county+' VS '+compare_zip+' in '+compare_county)
                tab1,tab2,tab3,tab4,tab5 = st.tabs(['Overall','People','Home','Work','Environment'])
                with tab1:
                    col1,col2=st.columns(2)
                    col1.subheader('Selected')
                    col1.write(selected_city)
                    col2.subheader('Similar')
                    col2.write(compare_city)
                    st.divider()
                    st.subheader('Similarity Scores')
                    col1,col2,col3,col4,col5=st.columns(5)
                    col1.metric('Overall',compare_record['OVERALL'][0].round(2))
                    col1.progress(compare_record['OVERALL'][0]/100)
                    col2.metric('People',compare_record['PEOPLE'][0].round(2))
                    col2.progress(compare_record['PEOPLE'][0]/100)
                    col3.metric('Home',compare_record['HOME'][0].round(2))
                    col3.progress(compare_record['HOME'][0]/100)
                    col4.metric('Work',compare_record['WORK'][0].round(2))
                    col4.progress(compare_record['WORK'][0]/100)
                    col5.metric('Environment',compare_record['ENVIRONMENT'][0].round(2))
                    col5.progress(compare_record['ENVIRONMENT'][0]/100)
                    df_long = pd.melt(compare_record[['OVERALL','PEOPLE','HOME','WORK','ENVIRONMENT']].reset_index(), id_vars=['index'], var_name='Categories', value_name='Scores')
                    fig = px.bar(df_long, x='Categories', y='Scores', color='Scores', color_continuous_scale='blues')
                    fig.update_layout(xaxis_title='Categories',
                    yaxis_title='Similarity Scores')
                    st.plotly_chart(fig,use_container_width=True)
                with tab2:
                    selected_record['PCT_18_65']=selected_record['PCT_OVER_18']-selected_record['PCT_OVER_65']
                    compare_record['PCT_18_65']=compare_record['PCT_OVER_18']-compare_record['PCT_OVER_65']
                    dif_cols=['MED_AGE','MED_HH_INC','PCT_POVERTY','PCT_BACH_MORE','POP_DENSITY','METRO_INDEX',
                        'HH_SIZE','FAM_SIZE','MED_HOME','MED_RENT','PCT_UNIT1','PCT_WORKING',
                        'MEAN_COMMUTE','PCT_WATER','ENV_INDEX','PCT_TOPARK_HALFMILE','PCT_TOPARK_ONEMILE']
                    dif_record=compare_record[dif_cols]-selected_record[dif_cols]
                    st.write(
                    """
                    <style>
                    [data-testid="stMetricDelta"] svg {
                    display: none;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                    )

                    col1,col2=st.columns(2)
                    col1.subheader('Selected')
                    col1.write(selected_city)
                    col2.subheader('Similar')
                    col2.write(compare_city)
                    st.divider()
                    col1,col2=st.columns(2)
                    fig = px.pie(selected_record, values=[selected_record['PCT_UNDER_18'][0], selected_record['PCT_18_65'][0], selected_record['PCT_OVER_65'][0]],names=['< 18','18-65','> 65'])
                    fig.update_layout(legend={'title': {'text': 'Age Distribution'}})
                    col1.caption('Selected')
                    col1.plotly_chart(fig,use_container_width=True)
                    fig = px.pie(compare_record, values=[compare_record['PCT_UNDER_18'][0], compare_record['PCT_18_65'][0], compare_record['PCT_OVER_65'][0]],names=['< 18','18-65','> 65'])
                    fig.update_layout(legend={'title': {'text': 'Age Distribution'}})
                    col2.caption('Similar')
                    col2.plotly_chart(fig,use_container_width=True)
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Median Age',selected_record['MED_AGE'][0].round(2))
                    col2.caption('Similar')
                    col2.metric('Median Age',compare_record['MED_AGE'][0].round(2),delta=dif_record['MED_AGE'][0].round(2))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Median Household Income','${:,.0f}'.format(selected_record['MED_HH_INC'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Median Household Income','${:,.0f}'.format(compare_record['MED_HH_INC'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_HH_INC'][0].round(2)))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Percent in Poverty','{:.1%}'.format(selected_record['PCT_POVERTY'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Percent in Poverty','{:.1%}'.format(compare_record['PCT_POVERTY'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_POVERTY'][0].round(2)/100))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Percent with Bachelors Degree or More','{:.1%}'.format(selected_record['PCT_BACH_MORE'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Percent with Bachelors Degree or More','{:.1%}'.format(compare_record['PCT_BACH_MORE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_BACH_MORE'][0].round(2)/100))    
                with tab3:
                    col1,col2=st.columns(2)
                    col1.subheader('Selected')
                    col1.write(selected_city)
                    col2.subheader('Similar')
                    col2.write(compare_city)
                    st.divider()
                    col1,col2=st.columns(2)
                    fig = px.pie(selected_record, values=[selected_record['PCT_OWN'][0], selected_record['PCT_RENT'][0]],names=['Percent Own Home','Percent Renting'])
                    fig.update_layout(legend={'title': {'text': 'Home Ownership'}})
                    col1.caption('Selected')
                    col1.plotly_chart(fig,use_container_width=True)
                    fig=px.pie(selected_record, values=[compare_record['PCT_OWN'][0], compare_record['PCT_RENT'][0]],names=['Percent Own Home','Percent Renting'])
                    fig.update_layout(legend={'title': {'text': 'Home Ownership'}})
                    col2.caption('Similar')
                    col2.plotly_chart(fig,use_container_width=True)
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Avg HH Size','{:,.1f}'.format(selected_record['HH_SIZE'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Avg HH Size','{:,.1f}'.format(compare_record['HH_SIZE'][0].round(2)),delta='{:,.1f}'.format(dif_record['HH_SIZE'][0].round(2)))
                    st.divider()
                    col1,col2=st.columns(2) 
                    col1.caption('Selected')
                    col1.metric('Avg Family Size','{:,.1f}'.format(selected_record['FAM_SIZE'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Avg Family Size','{:,.1f}'.format(compare_record['FAM_SIZE'][0].round(2)),delta='{:,.1f}'.format(dif_record['FAM_SIZE'][0].round(2)))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Median Home Price','${:,.0f}'.format(selected_record['MED_HOME'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Median Home Price','${:,.0f}'.format(compare_record['MED_HOME'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_HOME'][0].round(2)))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Median Rent Price','${:,.0f}'.format(selected_record['MED_RENT'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Median Rent Price','${:,.0f}'.format(compare_record['MED_RENT'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_RENT'][0].round(2)))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Pct Single Family Residential','{:.1%}'.format(selected_record['PCT_UNIT1'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Pct Single Family Residential','{:.1%}'.format(compare_record['PCT_UNIT1'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_UNIT1'][0].round(2)/100))
                with tab4:
                    col1,col2=st.columns(2)
                    col1.subheader('Selected')
                    col1.write(selected_city)
                    col2.subheader('Similar')
                    col2.write(compare_city)
                    st.divider()
                    col1,col2=st.columns(2)
                    fig = px.pie(selected_record, values=[selected_record['PCT_SERVICE'][0], selected_record['PCT_BC'][0],selected_record['PCT_WC'][0]],names=['Percent Service','Percent Blue Collar','Percent White Collar'])
                    fig.update_layout(legend={'title': {'text': 'Occupation Type'}})
                    col1.caption('Selected')
                    col1.plotly_chart(fig,use_container_width=True)
                    fig = px.pie(compare_record, values=[compare_record['PCT_SERVICE'][0], compare_record['PCT_BC'][0],compare_record['PCT_WC'][0]],names=['Percent Service','Percent Blue Collar','Percent White Collar'])
                    fig.update_layout(legend={'title': {'text': 'Occupation Type'}})
                    col2.caption('Similar')
                    col2.plotly_chart(fig,use_container_width=True)
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Pct Working','{:.1%}'.format(selected_record['PCT_WORKING'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Pct Working','{:.1%}'.format(compare_record['PCT_WORKING'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_WORKING'][0]/100))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Avg Commute Time',selected_record['MEAN_COMMUTE'][0].round(2))
                    col2.caption('Similar')
                    col2.metric('Avg Commute Time',compare_record['MEAN_COMMUTE'][0].round(2),delta='{:,.1f}'.format(dif_record['MEAN_COMMUTE'][0]))
                with tab5:
                    col1,col2=st.columns(2)
                    col1.subheader('Selected')
                    col1.write(selected_city)
                    col2.subheader('Similar')
                    col2.write(compare_city)
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.write('Location Type')
                    col1.write(selected_record['METROPOLITAN'][0])
                    col2.caption('Similar')
                    col2.write('Location Type')
                    col2.write(compare_record['METROPOLITAN'][0])
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Population Density','{:,.0f}'.format(selected_record['POP_DENSITY'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Population Density','{:,.0f}'.format(compare_record['POP_DENSITY'][0].round(2)),delta='{:.0f}'.format(dif_record['POP_DENSITY'][0]))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Pct Area is Water','{:.2%}'.format(selected_record['PCT_WATER'][0]))
                    col2.caption('Similar')
                    col2.metric('Pct Area is Water','{:.2%}'.format(compare_record['PCT_WATER'][0]),delta='{:.2%}'.format(dif_record['PCT_WATER'][0]))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Environmental Quality Index','{:.2f}'.format(selected_record['ENV_INDEX'][0].round(2)))
                    col2.caption('Similar')
                    col2.metric('Environmental Quality Index','{:.2f}'.format(compare_record['ENV_INDEX'][0].round(2)),delta='{:.2f}'.format(dif_record['ENV_INDEX'][0]))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Pct within 0.5 mile to Park','{:.1%}'.format(selected_record['PCT_TOPARK_HALFMILE'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Pct within 0.5 mile to Park','{:.1%}'.format(compare_record['PCT_TOPARK_HALFMILE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_TOPARK_HALFMILE'][0]/100))
                    st.divider()
                    col1,col2=st.columns(2)
                    col1.caption('Selected')
                    col1.metric('Pct within 1 mile to Park','{:.1%}'.format(selected_record['PCT_TOPARK_ONEMILE'][0].round(2)/100))
                    col2.caption('Similar')
                    col2.metric('Pct within 1 mile to Park','{:.1%}'.format(compare_record['PCT_TOPARK_ONEMILE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_TOPARK_ONEMILE'][0]/100))
                    
    
                   
    if zip_select != 'Zip':
        selected_record = master_zip[master_zip['ZIP']==zip_select].reset_index()
        selected_zip=selected_record['ZIP'][0]
        selected_county=selected_record['COUNTY_NAME'][0]
        selected_state=selected_record['STATE_SHORT'][0]

        #Columns for scaling
        PeopleCols_sc=['MED_AGE_SC','PCT_UNDER_18_SC','MED_HH_INC_SC', 'PCT_POVERTY_SC','PCT_BACH_MORE_SC']
        HomeCols_sc=['HH_SIZE_SC','PCT_OWN_SC','MED_HOME_SC','PCT_UNIT1_SC','PCT_UNIT24_SC']
        WorkCols_sc=['MEAN_COMMUTE_SC','PCT_WC_SC','PCT_WORKING_SC','PCT_SERVICE_SC','PCT_BC_SC']
        EnvironmentCols_sc=['PCT_WATER_SC','ENV_INDEX_SC','PCT_TOPARK_ONEMILE_SC','POP_DENSITY_SC','METRO_INDEX_SC']

        # Calculate the euclidian distance between the selected record and the rest of the dataset
        People_dist             = euclidean_distances(filt_master_zip.loc[:, PeopleCols_sc], selected_record[PeopleCols_sc].values.reshape(1, -1))
        Home_dist               = euclidean_distances(filt_master_zip.loc[:, HomeCols_sc], selected_record[HomeCols_sc].values.reshape(1, -1))
        Work_dist               = euclidean_distances(filt_master_zip.loc[:, WorkCols_sc], selected_record[WorkCols_sc].values.reshape(1, -1))
        Environment_dist        = euclidean_distances(filt_master_zip.loc[:, EnvironmentCols_sc], selected_record[EnvironmentCols_sc].values.reshape(1, -1))

        # Create a new dataframe with the similarity scores and the corresponding index of each record
        df_similarity = pd.DataFrame({'PEOPLE_SIM': People_dist [:, 0],'HOME_SIM': Home_dist [:, 0],'WORK_SIM': Work_dist [:, 0],'ENV_SIM': Environment_dist [:, 0], 'index': filt_master_zip.index})

        #df_similarity['OVERALL_SIM']=df_similarity['PEOPLE_SIM','HOME_SIM','WORK_SIM','ENV_SIM'].mean(axis=1)
        weights=[people_select,home_select,work_select,environment_select]
        # Multiply column values with weights
        df_weighted = df_similarity.loc[:, ['PEOPLE_SIM', 'HOME_SIM', 'WORK_SIM','ENV_SIM']].mul(weights)
        df_similarity['OVERALL_W']=df_weighted.sum(axis=1)/sum(weights)

        people_max=df_similarity['PEOPLE_SIM'].max()
        home_max=df_similarity['HOME_SIM'].max()
        work_max=df_similarity['WORK_SIM'].max()
        env_max=df_similarity['ENV_SIM'].max()
        overall_max=df_similarity['OVERALL_W'].max()

        df_similarity['PEOPLE']  = 100 - (100 * df_similarity['PEOPLE_SIM'] / people_max)
        df_similarity['HOME']    = 100 - (100 * df_similarity['HOME_SIM'] / home_max)
        df_similarity['WORK']    = 100 - (100 * df_similarity['WORK_SIM'] / work_max)
        df_similarity['ENVIRONMENT']     = 100 - (100 * df_similarity['ENV_SIM'] / env_max)
        df_similarity['OVERALL'] = 100 - (100 * df_similarity['OVERALL_W'] / overall_max)

        # Sort the dataframe by the similarity scores in descending order and select the top 10 most similar records
        df_similarity = df_similarity.sort_values(by='OVERALL_W', ascending=True).head(count_select+1)

        # Merge the original dataframe with the similarity dataframe to display the top 10 most similar records
        df_top10 = pd.merge(df_similarity, filt_master_zip, left_on='index', right_index=True).reset_index(drop=True)
        df_top10=df_top10.loc[1:count_select]
        df_top10['RANK']=list(range(1,count_select+1))
        df_top10['RANKING']=df_top10['RANK'].astype(str)+' - Zip Code '+df_top10['ZIP']+' from '+df_top10['COUNTY_NAME']+' County, '+df_top10['STATE_SHORT']
        df_top10['LAT_R']=selected_record['LAT'][0]
        df_top10['LON_R']=selected_record['LON'][0]
        df_top10['SAVE']=False
        df_top10['NOTES']=''

        st.header('Top '+'{}'.format(count_select)+' Most Similar Locations')
        #st.write('You selected zip code '+zip_select+' from '+selected_record['County Title'][0])
        # CSS to inject contained in a string
        hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        tab1,tab2=st.tabs(['Map','Data'])
        with tab2:
            with st.expander('Expand for Table Info'):
                st.markdown(
                """
                - The values for OVERALL, PEOPLE, HOME, WORK, and ENVIRONMENT are scaled similarity scores for the respective categories with values of 0-100, where 100 represents a perfect match.
                - Locations are ranked by their OVERALL score, which is a weighted average of the individual category scores.
                - Save your research by checking locations in the SAVE column which will be added to csv for download.
                """
                )
            @st.cache_data
            def convert_df(df):
                return df.to_csv().encode('utf-8')
            df_top10['COUNTY_STATE']=df_top10['COUNTY_NAME']+' County, '+df_top10['STATE_SHORT']
            cols=['ZIP','COUNTY_STATE','RANK','OVERALL','PEOPLE','HOME','WORK','ENVIRONMENT']
            df=df_top10[cols+['SAVE','NOTES']]
            df=df.set_index('RANK')
            edited_df=st.experimental_data_editor(df)
            save=edited_df[edited_df['SAVE']==True]
            save=save.reset_index()
            csv = convert_df(save[cols+['SAVE','NOTES']])
            st.download_button(label="Download Selections as CSV",data=csv,file_name='SIMILO_SAVED.csv',mime='text/csv',)
        with tab1:
            latcenter=df_top10['LAT'].mean()
            loncenter=df_top10['LON'].mean()
            #map token for additional map layers
            token = "pk.eyJ1Ijoia3NvZGVyaG9sbTIyIiwiYSI6ImNsZjI2djJkOTBmazU0NHBqdzBvdjR2dzYifQ.9GkSN9FUYa86xldpQvCvxA" # you will need your own token
            #mapbox://styles/mapbox/streets-v12
            fig1 = px.scatter_mapbox(df_top10, lat='LAT',lon='LON',center=go.layout.mapbox.Center(lat=latcenter,lon=loncenter),
                                    color="RANK", color_continuous_scale=px.colors.sequential.ice, hover_name='ZIP', hover_data=['RANK','COUNTY_NAME'],zoom=3,)
            fig1.update_traces(marker={'size': 15})
            fig1.update_layout(mapbox_style="mapbox://styles/mapbox/satellite-streets-v12",
                               mapbox_accesstoken=token)
            fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig1,use_container_width=True)

        st.divider()

        st.header('Location Deep Dive')
        rank_select=st.selectbox('Select from rankings above',list(df_top10['RANKING']))
        if rank_select:
            compare_record=df_top10[df_top10['RANKING']==rank_select].reset_index(drop=True)
            compare_zip=compare_record['ZIP'][0]
            compare_county=compare_record['COUNTY_NAME'][0]
            compare_state=compare_record['STATE_SHORT'][0]
            #st.write(selected_zip+' in '+selected_county+' VS '+compare_zip+' in '+compare_county)
            tab1,tab2,tab3,tab4,tab5 = st.tabs(['Overall','People','Home','Work','Environment'])
            with tab1:
                col1,col2=st.columns(2)
                col1.subheader('Selected')
                col1.write(selected_zip+' in '+selected_county+' County, '+selected_state)
                col2.subheader('Similar')
                col2.write(compare_zip+' in '+compare_county+' County, '+compare_state)
                st.divider()
                st.subheader('Similarity Scores')
                col1,col2,col3,col4,col5=st.columns(5)
                col1.metric('Overall',compare_record['OVERALL'][0].round(2))
                col1.progress(compare_record['OVERALL'][0]/100)
                col2.metric('People',compare_record['PEOPLE'][0].round(2))
                col2.progress(compare_record['PEOPLE'][0]/100)
                col3.metric('Home',compare_record['HOME'][0].round(2))
                col3.progress(compare_record['HOME'][0]/100)
                col4.metric('Work',compare_record['WORK'][0].round(2))
                col4.progress(compare_record['WORK'][0]/100)
                col5.metric('Environment',compare_record['ENVIRONMENT'][0].round(2))
                col5.progress(compare_record['ENVIRONMENT'][0]/100)
                df_long = pd.melt(compare_record[['OVERALL','PEOPLE','HOME','WORK','ENVIRONMENT']].reset_index(), id_vars=['index'], var_name='Categories', value_name='Scores')
                fig = px.bar(df_long, x='Categories', y='Scores', color='Scores', color_continuous_scale='blues')
                fig.update_layout(xaxis_title='Categories',
                  yaxis_title='Similarity Scores')
                st.plotly_chart(fig,use_container_width=True)
            with tab2:
                selected_record['PCT_18_65']=selected_record['PCT_OVER_18']-selected_record['PCT_OVER_65']
                compare_record['PCT_18_65']=compare_record['PCT_OVER_18']-compare_record['PCT_OVER_65']
                dif_cols=['MED_AGE','MED_HH_INC','PCT_POVERTY','PCT_BACH_MORE','POP_DENSITY','METRO_INDEX',
                        'HH_SIZE','FAM_SIZE','MED_HOME','MED_RENT','PCT_UNIT1','PCT_WORKING',
                        'MEAN_COMMUTE','PCT_WATER','ENV_INDEX','PCT_TOPARK_HALFMILE','PCT_TOPARK_ONEMILE']
                dif_record=compare_record[dif_cols]-selected_record[dif_cols]
                st.write(
                """
                <style>
                [data-testid="stMetricDelta"] svg {
                display: none;
                }
                </style>
                """,
                unsafe_allow_html=True,
                )
                col1,col2=st.columns(2)
                col1.subheader('Selected')
                col1.write(selected_zip+' in '+selected_county+' County, '+selected_state)
                col2.subheader('Similar')
                col2.write(compare_zip+' in '+compare_county+' County, '+compare_state)
                st.divider()
                col1,col2=st.columns(2)
                fig = px.pie(selected_record, values=[selected_record['PCT_UNDER_18'][0], selected_record['PCT_18_65'][0], selected_record['PCT_OVER_65'][0]],names=['< 18','18-65','> 65'])
                fig.update_layout(legend={'title': {'text': 'Age Distribution'}})
                col1.caption('Selected')
                col1.plotly_chart(fig,use_container_width=True)
                fig = px.pie(compare_record, values=[compare_record['PCT_UNDER_18'][0], compare_record['PCT_18_65'][0], compare_record['PCT_OVER_65'][0]],names=['< 18','18-65','> 65'])
                fig.update_layout(legend={'title': {'text': 'Age Distribution'}})
                col2.caption('Similar')
                col2.plotly_chart(fig,use_container_width=True)
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Median Age',selected_record['MED_AGE'][0].round(2))
                col2.caption('Similar')
                col2.metric('Median Age',compare_record['MED_AGE'][0].round(2),delta=dif_record['MED_AGE'][0].round(2))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Median Household Income','${:,.0f}'.format(selected_record['MED_HH_INC'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Median Household Income','${:,.0f}'.format(compare_record['MED_HH_INC'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_HH_INC'][0].round(2)))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Percent in Poverty','{:.1%}'.format(selected_record['PCT_POVERTY'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Percent in Poverty','{:.1%}'.format(compare_record['PCT_POVERTY'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_POVERTY'][0].round(2)/100))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Percent with Bachelors Degree or More','{:.1%}'.format(selected_record['PCT_BACH_MORE'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Percent with Bachelors Degree or More','{:.1%}'.format(compare_record['PCT_BACH_MORE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_BACH_MORE'][0].round(2)/100))    
            with tab3:
                col1,col2=st.columns(2)
                col1.subheader('Selected')
                col1.write(selected_zip+' in '+selected_county+' County, '+selected_state)
                col2.subheader('Similar')
                col2.write(compare_zip+' in '+compare_county+' County, '+compare_state)
                st.divider()
                col1,col2=st.columns(2)
                fig = px.pie(selected_record, values=[selected_record['PCT_OWN'][0], selected_record['PCT_RENT'][0]],names=['Percent Own Home','Percent Renting'])
                fig.update_layout(legend={'title': {'text': 'Home Ownership'}})
                col1.caption('Selected')
                col1.plotly_chart(fig,use_container_width=True)
                fig=px.pie(selected_record, values=[compare_record['PCT_OWN'][0], compare_record['PCT_RENT'][0]],names=['Percent Own Home','Percent Renting'])
                fig.update_layout(legend={'title': {'text': 'Home Ownership'}})
                col2.caption('Similar')
                col2.plotly_chart(fig,use_container_width=True)
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Avg HH Size','{:,.1f}'.format(selected_record['HH_SIZE'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Avg HH Size','{:,.1f}'.format(compare_record['HH_SIZE'][0].round(2)),delta='{:,.1f}'.format(dif_record['HH_SIZE'][0].round(2)))
                st.divider()
                col1,col2=st.columns(2) 
                col1.caption('Selected')
                col1.metric('Avg Family Size','{:,.1f}'.format(selected_record['FAM_SIZE'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Avg Family Size','{:,.1f}'.format(compare_record['FAM_SIZE'][0].round(2)),delta='{:,.1f}'.format(dif_record['FAM_SIZE'][0].round(2)))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Median Home Price','${:,.0f}'.format(selected_record['MED_HOME'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Median Home Price','${:,.0f}'.format(compare_record['MED_HOME'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_HOME'][0].round(2)))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Median Rent Price','${:,.0f}'.format(selected_record['MED_RENT'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Median Rent Price','${:,.0f}'.format(compare_record['MED_RENT'][0].round(2)),delta='${:,.0f}'.format(dif_record['MED_RENT'][0].round(2)))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Pct Single Family Residential','{:.1%}'.format(selected_record['PCT_UNIT1'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Pct Single Family Residential','{:.1%}'.format(compare_record['PCT_UNIT1'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_UNIT1'][0].round(2)/100))
            with tab4:
                col1,col2=st.columns(2)
                col1.subheader('Selected')
                col1.write(selected_zip+' in '+selected_county+' County, '+selected_state)
                col2.subheader('Similar')
                col2.write(compare_zip+' in '+compare_county+' County, '+compare_state)
                st.divider()
                col1,col2=st.columns(2)
                fig = px.pie(selected_record, values=[selected_record['PCT_SERVICE'][0], selected_record['PCT_BC'][0],selected_record['PCT_WC'][0]],names=['Percent Service','Percent Blue Collar','Percent White Collar'])
                fig.update_layout(legend={'title': {'text': 'Occupation Type'}})
                col1.caption('Selected')
                col1.plotly_chart(fig,use_container_width=True)
                fig = px.pie(compare_record, values=[compare_record['PCT_SERVICE'][0], compare_record['PCT_BC'][0],compare_record['PCT_WC'][0]],names=['Percent Service','Percent Blue Collar','Percent White Collar'])
                fig.update_layout(legend={'title': {'text': 'Occupation Type'}})
                col2.caption('Similar')
                col2.plotly_chart(fig,use_container_width=True)
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Pct Working','{:.1%}'.format(selected_record['PCT_WORKING'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Pct Working','{:.1%}'.format(compare_record['PCT_WORKING'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_WORKING'][0]/100))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Avg Commute Time',selected_record['MEAN_COMMUTE'][0].round(2))
                col2.caption('Similar')
                col2.metric('Avg Commute Time',compare_record['MEAN_COMMUTE'][0].round(2),delta='{:,.1f}'.format(dif_record['MEAN_COMMUTE'][0]))
            with tab5:
                col1,col2=st.columns(2)
                col1.subheader('Selected')
                col1.write(selected_zip+' in '+selected_county+' County, '+selected_state)
                col2.subheader('Similar')
                col2.write(compare_zip+' in '+compare_county+' County, '+compare_state)
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.write('Location Type')
                col1.write(selected_record['METROPOLITAN'][0])
                col2.caption('Similar')
                col2.write('Location Type')
                col2.write(compare_record['METROPOLITAN'][0])
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Population Density','{:,.0f}'.format(selected_record['POP_DENSITY'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Population Density','{:,.0f}'.format(compare_record['POP_DENSITY'][0].round(2)),delta='{:.0f}'.format(dif_record['POP_DENSITY'][0]))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Pct Area is Water','{:.2%}'.format(selected_record['PCT_WATER'][0]))
                col2.caption('Similar')
                col2.metric('Pct Area is Water','{:.2%}'.format(compare_record['PCT_WATER'][0]),delta='{:.2%}'.format(dif_record['PCT_WATER'][0]))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Environmental Quality Index','{:.2f}'.format(selected_record['ENV_INDEX'][0].round(2)))
                col2.caption('Similar')
                col2.metric('Environmental Quality Index','{:.2f}'.format(compare_record['ENV_INDEX'][0].round(2)),delta='{:.2f}'.format(dif_record['ENV_INDEX'][0]))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Pct within 0.5 mile to Park','{:.1%}'.format(selected_record['PCT_TOPARK_HALFMILE'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Pct within 0.5 mile to Park','{:.1%}'.format(compare_record['PCT_TOPARK_HALFMILE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_TOPARK_HALFMILE'][0]/100))
                st.divider()
                col1,col2=st.columns(2)
                col1.caption('Selected')
                col1.metric('Pct within 1 mile to Park','{:.1%}'.format(selected_record['PCT_TOPARK_ONEMILE'][0].round(2)/100))
                col2.caption('Similar')
                col2.metric('Pct within 1 mile to Park','{:.1%}'.format(compare_record['PCT_TOPARK_ONEMILE'][0].round(2)/100),delta='{:.1%}'.format(dif_record['PCT_TOPARK_ONEMILE'][0]/100))
                                 

#About Page
if selected=='Team':
    
    st.title('About Us')
    with st.container():
        col1,col2=st.columns(2)
        col1.write('')
        col1.write('')
        col1.write('')
        col1.subheader('김서린')
        col1.write('M.S. Student @ SNU GSDS')
        col1.write('[github](https://github.com/Seorin-Kim)')
        col2.image('./photo/mung.jpeg', width = 300)
    
    st.divider()
    
    with st.container():
        col1,col2=st.columns(2)
        col1.image('./photo/mungmung.jpeg', width = 270)
        col2.write('')
        col2.write('')
        col2.write('')
        col2.subheader('박선호')
        col2.write('M.S. Student @ SNU GSDS')
        col2.write('[github](https://github.com/preferpark99)')

    st.divider()
    with st.container():
        col1,col2=st.columns(2)
        col1.write('')
        col1.write('')
        col1.write('')
        col1.subheader('박지형')
        col1.write('M.S. Student @ SNU GSDS')
        col1.write('[github](https://github.com/ImPJH)')
        col2.image('./photo/mung.jpeg', width = 300)
    
    st.divider()
    
    with st.container():
        col1,col2=st.columns(2)
        col1.image('./photo/mungmung.jpeg', width = 270)
        col2.write('')
        col2.write('')
        col2.write('')
        col2.subheader('이나은')
        col2.write('M.S. Student @ SNU GSDS')
        col2.write('[github](https://github.com/better62)')

    st.divider()
    with st.container():
        col1,col2=st.columns(2)
        col1.write('')
        col1.write('')
        col1.write('')
        col1.subheader('진현빈')
        col1.write('M.S. Student @ SNU GSDS')
        col1.write('[github](https://github.com/hyunbinui)')
        col2.image('./photo/mung.jpeg', width = 300)    
