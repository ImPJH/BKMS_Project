import pandas as pd
import folium

airbnb = pd.read_csv('./data/airbnb_preprocessed.csv')
attraction = pd.read_csv('./data/merged_attraction.csv')
heatmap = pd.read_csv('./data/precinct_danger_normalized.csv')

geo_data = './data/neighbourhoods.geojson'
latitude, longitude = airbnb['latitude'].values[0], airbnb['longitude'].values[0]
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

airbnb = airbnb.sort_values(by='airbnb_danger')
folium.Circle(
    location = airbnb.loc[1, ['latitude', 'longitude']],
    tooltip = airbnb.loc[1, 'name'],        # 마우스 갖다대면 나오는 문구
    popup = folium.Popup(f"{airbnb.loc[1, 'description']}", max_width=300, min_width=300),
    radius = 150,
    color='darkred',
    opacity=0.65
).add_to(m)

m