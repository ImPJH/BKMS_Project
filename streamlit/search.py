import streamlit as st

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.neighbourhood_api as neighbourhood_api
import name_api
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import json


st.set_page_config(
    page_title="SEARCH",
    layout="wide",
    page_icon="🫂",
    initial_sidebar_state="expanded")

show_pages([
    Page("page.py","Main"),
    Page("login.py","login"),
    Page("team.py","Team"),
    Page("search.py","Search"),
    Page("listpage.py","Listpage")
])

hide_pages(['login', 'Main', 'Team','Search','Listpage'])

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search','Team'],
        icons=['house','search','people'],menu_icon='airplane', default_index=1)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')

if selected == "Search":
    st.subheader('Search Your Airbnb!') #위에 부제목

    #neighbourhood, accommodation table 가져와서 필요한 column만 쓰는거 sql문으로 구현해야됨?

    loc_select=st.radio('Type',['Location으로 검색','Airbnb name으로 검색'],horizontal=True, label_visibility="collapsed") 

    if loc_select=='Airbnb name으로 검색':
        #text로 검색하는 부분 구현해야됨
        text_input = st.text_input("Enter Your Airbnb name : ")
        if text_input:
            name_id, name_list = name_api.search_from_name(text_input)
            print(name_id,name_list)

    if loc_select=='Location으로 검색':
        group_list = neighbourhood_api.get_distinct_neighbourhood_group(to_list=True)
        neighbourhood_group_select = st.selectbox(label='Borough',options=['Borough']+group_list, label_visibility='collapsed')

        neighbourhood_list = neighbourhood_api.get_neighbourhood_in_neighbourhood_group(neighbourhood_group_select,to_list=True)
        neighbourhood_select = st.selectbox(label='Neighbourhood',options=['Neighbourhood']+neighbourhood_list, label_visibility='collapsed')

    if st.button('OK'):
        switch_page('Listpage')
        #5개 중 하나의 neighbourhood 택하면 더 세부 neighbourhood 선택하는거 구현해야됨

    #범죄 위험도 몇 미만인 숙소 검색 부분도 시간 되면 구현하기

else:
    switch_page(selected)