import streamlit as st

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.neighbourhood_api as neighbourhood_api
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import json

hide_pages(['login', 'Main', 'Team','Search'])

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search','Team'],
        icons=['play-btn','search','info-circle'],menu_icon='intersect', default_index=1)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')

if selected == "Main":
    switch_page('Main')

if selected == "Team":
    switch_page("Team")

st.title('Search Your Airbnb!') #위에 부제목

#neighbourhood, accommodation table 가져와서 필요한 column만 쓰는거 sql문으로 구현해야됨?

loc_select=st.radio('Type',['Location으로 검색','Airbnb name으로 검색'],horizontal=True, label_visibility="collapsed") 

if loc_select=='Airbnb name으로 검색':
    #text로 검색하는 부분 구현해야됨
    pass
if loc_select=='Location으로 검색':
    group_list = neighbourhood_api.get_distinct_neighbourhood_group(to_list=True)
    neighbourhood_group_select = st.selectbox(label='Borough',options=['Borough']+group_list, label_visibility='collapsed')

    neighbourhood_list = neighbourhood_api.get_neighbourhood_in_neighbourhood_group(neighbourhood_group_select,to_list=True)
    neighbourhood_select = st.selectbox(label='Neighbourhood',options=['Neighbourhood']+neighbourhood_list, label_visibility='collapsed')

# st.button('OK')
    #5개 중 하나의 neighbourhood 택하면 더 세부 neighbourhood 선택하는거 구현해야됨

#범죄 위험도 몇 미만인 숙소 검색 부분도 시간 되면 구현하기

#이런 코드도 있는데.. 참고
# # SQLite 데이터베이스 연결
# conn = sqlite3.connect('database.db')
# c = conn.cursor()

# # accommodation.csv 파일에서 'name' 열 가져오기
# accommodation_data = pd.read_csv('accommodation.csv')
# accommodation_data.to_sql('accommodation', conn, if_exists='replace', index=False)

# # neighbourhood.csv 파일에서 'neighbourhood'와 'neighbourhood_group' 열 가져오기
# neighbourhood_data = pd.read_csv('neighbourhood.csv')
# neighbourhood_data.to_sql('neighbourhood', conn, if_exists='replace', index=False)

# # Streamlit 앱 구현
# if st.button('Get Columns'):
#     selected_column = st.selectbox('Select Column', ['name', 'neighbourhood', 'neighbourhood_group'])
    
#     if selected_column == 'name':
#         result = c.execute('SELECT name FROM accommodation').fetchall()
#         st.write(result)
#     elif selected_column == 'neighbourhood':
#         result = c.execute('SELECT neighbourhood FROM neighbourhood').fetchall()
#         st.write(result)
#     elif selected_column == 'neighbourhood_group':
#         result = c.execute('SELECT neighbourhood_group FROM neighbourhood').fetchall()
#         st.write(result)


#사용자가 선택한 것에 맞춰 필터링 완료 후 불러오는 작업 구현해야 됨
# filt_master_neighbourhood=neighbourhood
# filt_master_accommodation=accommodation
# if len(state_select)>0:
#     filt_master_neighbourhood=neighbourhood[neighbourhood['STATE_LONG'].isin(state_select)]
#     filt_master_accommodation=accommodation[accommodation['STATE_LONG'].isin(state_select)]


#새로운 페이지에서(?) 왼쪽에 적절한 핀포인트가 찍힌 지도와 함께 오른쪽에 그에 해당하는 숙소 + 추천 숙소 list 보여주기
#특정 숙소를 클릭하면 범죄 관련 부분 통계 함께 밑 부분에 보여주는..    
#About Page