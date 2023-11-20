import streamlit as st

import pandas as pd
import geopandas as gpd

import folium
from folium.map import Marker
from streamlit_folium import st_folium

from jinja2 import Template




### streamlit 기본 지도에 숙소 빨간 마커로 찍기

airbnb = pd.read_csv('listings.csv')
st.map(airbnb)




### streamlit-folium 사용
### 마커 클릭하면 alert, 아직 지도가 안 뜨는 문제

# Modify Marker template to include the onClick event
click_template = """{% macro script(this, kwargs) %}
function onClick(e) {
                 let point = e.latlng; alert(point)
                 }
                 
    var {{ this.get_name() }} = L.marker(
        {{ this.location|tojson }},
        {{ this.options|tojson }}
    ).addTo({{ this._parent.get_name() }}).on('click', onClick);
{% endmacro %}"""

click_js = """function onClick(e) {
                 var point = e.latlng; alert(point)
                 }"""

# Change template to custom template
Marker._template = Template(click_template)

center = [40.664167, -73.938611]    # new york city 위도,경도
m = folium.Map(location=center, zoom_start=10)

e = folium.Element(click_js)
html = m.get_root()
html.script.get_root().render()
html.script._children[e.get_name()] = e

#Add marker (click on map an alert will display with latlng values)
marker = folium.Marker(center).add_to(m)

st_folium(m, width=750)




### folium 사용
### geojson 파일 + neighbourhoods별로 danger 컬럼 가지는 csv 파일 -> 히트맵으로 시각화하기
### airbnb 숙소 데이터로 room_type에 따라 색상 다르게 해서 마커 찍기

### [Make this Notebook Trusted to load map: File -> Trust Notebook] 오류
### -> 안될 때마다 터미널에 'pip3 install branca==0.3.1'

airbnb = pd.read_csv('listings.csv')
heatmap = pd.read_csv('neighbourhoods_heatmap_example.csv')
geo_data = 'neighbourhoods.geojson'
center = [40.664167, -73.938611]    # new york city 위도,경도

m = folium.Map(location=center, zoom_start=10)

# 히트맵
folium.Choropleth(
    geo_data=geo_data,      # .geojson 파일
    data=heatmap,           # .csv 파일
    columns=('neighbourhood', 'danger'), 
    key_on='feature.properties.neighbourhood',
    fill_color='BuPu',
    legend_name='위험도',
).add_to(m)

# folium으로 500개 -> 안 뜸 ... 가장 문제
for i in airbnb.index[:400]:
    if airbnb['room_type'][i] == 'Private room':
        folium.Circle(
            location = airbnb.loc[i, ['latitude', 'longitude']],
            tooltip = airbnb.loc[i, 'name'],        # 마우스 갖다대면 나오는 문구
            popup = airbnb.loc[i, 'description'],   # 클릭하면 나오는 문구
            radius = 50,
            color='red'
        ).add_to(m)
    
    elif airbnb['room_type'][i] == 'Entire home/apt':
        folium.Circle(
            location = airbnb.loc[i, ['latitude', 'longitude']],
            tooltip = airbnb.loc[i, 'name'],
            popup = airbnb.loc[i, 'description'],
            radius = 50,
            color='blue'
        ).add_to(m)
    
    elif airbnb['room_type'][i] == 'Shared room':
        folium.Circle(
            location = airbnb.loc[i, ['latitude', 'longitude']],
            tooltip = airbnb.loc[i, 'name'],
            popup = airbnb.loc[i, 'description'],
            radius = 50,
            color='green'
        ).add_to(m)
    
    elif airbnb['room_type'][i] == 'Hotel room':
        folium.Circle(
            location = airbnb.loc[i, ['latitude', 'longitude']],
            tooltip = airbnb.loc[i, 'name'],
            popup = airbnb.loc[i, 'description'],
            radius = 50,
            color='yellow'
        ).add_to(m)

m