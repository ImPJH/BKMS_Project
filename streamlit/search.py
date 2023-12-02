import streamlit as st

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.neighbourhood_api as neighbourhood_api
import apis.price_api as price_api
import apis.danger_api as danger_api
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    col1, col2, col3 = st.sidebar.columns(3)
    if col1.button('My Page', key='mypage'):
        st.session_state.page = 'mypage'
        switch_page('login')
    if col2.button('Logout', key='logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = 'login'
        switch_page('Main')
    
else:
    if st.sidebar.button('Login', key='login'):
        switch_page('login')



@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search', 'Airbnb Info', 'Team'],
        icons=['house','search', 'list-ul', 'people'],menu_icon='airplane', default_index=1)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie, key='loc')



if selected == "Main":
    switch_page('Main')


if selected == "Search":
    st.session_state['list_accommodation_id'] = None

    st.subheader('Search Your Airbnb!') #위에 부제목

    #neighbourhood, accommodation table 가져와서 필요한 column만 쓰는거 sql문으로 구현해야됨?

    loc_select=st.radio('Type',['Location','Airbnb Name','Price','Danger'],horizontal=True, label_visibility="collapsed") 

    if loc_select=='Airbnb Name':
        text_input = st.text_input("Enter Your Airbnb name : ")

        if st.button('OK'):
            if text_input:
                name_id, name_list = name_api.search_from_name(text_input)
                if name_id  in name_list:
                    name_list.remove(name_id)
                name_list.insert(0,name_id)

                st.session_state['list_accommodation_id'] = name_list
                st.session_state['accommodation_id'] = name_id
                switch_page('Listpage')

    if loc_select=='Location':
        if 'min_price' not in st.session_state:
            st.session_state['min_price'] = 10
        if 'max_price' not in st.session_state:
            st.session_state['max_price'] = 300

        group_list = neighbourhood_api.get_distinct_neighbourhood_group(to_list=True)
        neighbourhood_group_select = st.selectbox(label='Borough',options=['Borough']+group_list, label_visibility='collapsed')

        neighbourhood_list = neighbourhood_api.get_neighbourhood_in_neighbourhood_group(neighbourhood_group_select,to_list=True)
        neighbourhood_select = st.selectbox(label='Neighbourhood',options=['Neighbourhood']+neighbourhood_list, label_visibility='collapsed')
        
        # with st.expander('Select price range'):
        #     min_price, max_price = st.slider("💸 Select a range of price ($)", 0, 300, 
        #                                 (st.session_state['min_price'], st.session_state['max_price']), 
        #                                 key='price_range_slider')
        # # st.session_state['min_price'] = min_price
        # # st.session_state['max_price'] = max_price

        if st.button('OK'):
            list_accommodation_id = neighbourhood_api.get_accommodation_id_by_neighbourhoods(neighbourhood_select,neighbourhood_group_select,min_price, max_price, to_list=True)
            st.session_state['list_accommodation_id'] = list_accommodation_id
            st.session_state['accommodation_id'] = None
            switch_page('Listpage')
    
    # if loc_select=='Search by Price':
        
    #     if 'min_price' not in st.session_state:
    #         st.session_state['min_price'] = 10
    #     if 'max_price' not in st.session_state:
    #         st.session_state['max_price'] = 300
        
    #     st.session_state['min_price'] = st.number_input("💸 Enter minimum price (unit:💲) : ", min_value = 10, max_value=300, 
    #                                                     value=st.session_state['min_price'],key='min_price_input')
    #     st.session_state['max_price'] = st.number_input("💸 Enter maximum price (unit:💲) : ", min_value = 10, max_value=300, 
    #                                                     value=st.session_state['max_price'],key='max_price_input')
        
    #     st.session_state['min_price'], st.session_state['max_price'] = st.slider("Or, Select a range of price", 10, 300, 
    #                                      (st.session_state['min_price'], st.session_state['max_price']), key = 'price_range_slider')
    #     if st.button('OK'):
    #         list_accommodation_id = price_api.get_price(st.session_state['min_price'],st.session_state['max_price'],to_list=True)
    #         st.session_state['list_accommodation_id'] = list_accommodation_id
    #         st.session_state['accommodation_id'] = None
    #         switch_page('Listpage')

    if loc_select=='Price':
        if 'min_price' not in st.session_state:
            st.session_state['min_price'] = 0
        if 'max_price' not in st.session_state:
            st.session_state['max_price'] = 300
        # if 'input_type_price' not in st.session_state:
        #     st.session_state['input_type_price'] = 'slider'

        # input_type_price = st.selectbox("Choose your input type", ['slider', 'text'], index=['slider', 'text'].index(st.session_state['input_type_price']), key='input_type_price')

        # if input_type_price == 'slider':
        min_price, max_price = st.slider("💸 Select a range of price ($)", 0, 300, 
                                        (st.session_state['min_price'], st.session_state['max_price']), 
                                        key='price_range_slider')
        st.session_state['min_price'] = min_price
        st.session_state['max_price'] = max_price
        # else:
        #     col1, col2, col3 = st.columns([4.5,1,4.5])
        #     with col1:
        #         st.session_state['min_price'] = st.number_input("💸 Enter minimum price ($) : ", min_value = 10, max_value=300, 
        #                                                         value=st.session_state['min_price'],key='min_price_input')
        #     with col2:
        #         st.write("\n")
        #         st.markdown("**<center>~</center>**", unsafe_allow_html=True)
        #     with col3:
        #         st.session_state['max_price'] = st.number_input("💸 Enter maximum price ($) : ", min_value = 10, max_value=300, 
        #                                                         value=st.session_state['max_price'],key='max_price_input')
        order_by = st.selectbox("Order by", ['Danger', 'Price'], index=0, key='order_by')

        if st.button('OK'):
            list_accommodation_id = price_api.get_price(st.session_state['min_price'],st.session_state['max_price'], order_by, to_list=True)
            if not list_accommodation_id:
                st.write("해당 범위에는 숙소가 존재하지 않습니다.")
            else:
                st.session_state['list_accommodation_id'] = list_accommodation_id
                st.session_state['accommodation_id'] = None
                switch_page('Listpage')



    # if loc_select=='Search by Danger':
        
    #     if 'min_danger' not in st.session_state:
    #         st.session_state['min_danger'] = 0.0
    #     if 'max_danger' not in st.session_state:
    #         st.session_state['max_danger'] = 100.0
        
    #     st.session_state['min_danger'] = st.number_input("🚨 Enter minimum danger : ", min_value = 0.0, max_value=100.0, 
    #                                                     value=st.session_state['min_danger'],key='min_danger_input')
    #     st.session_state['max_danger'] = st.number_input("🚨 Enter maximum danger : ", min_value = 0.0, max_value=100.0, 
    #                                                     value=st.session_state['max_danger'],key='max_danger_input')
        
    #     st.session_state['min_danger'], st.session_state['max_danger'] = st.slider("Or, Select a range of danger", 0.0, 100.0, 
    #                                      (st.session_state['min_danger'], st.session_state['max_danger']), key = 'price_range_slider')
    #     if st.button('OK'):
    #         list_accommodation_id = danger_api.get_danger(st.session_state['min_danger'],st.session_state['max_danger'],to_list=True)
    #         st.session_state['list_accommodation_id'] = list_accommodation_id
    #         st.session_state['accommodation_id'] = None
    #         switch_page('Listpage')

    if loc_select=='Danger':
        st.markdown("**:red[Danger의 기준]**")
        st.markdown("→ Airbnb danger와 Precinct danger를 평균 낸 것 (0점~100점)")
        st.markdown("\n")
        if 'min_danger' not in st.session_state:
            st.session_state['min_danger'] = 0.0
        if 'max_danger' not in st.session_state:
            st.session_state['max_danger'] = 100.0
        # if 'input_type' not in st.session_state:
        #     st.session_state['input_type'] = 'slider'

        # input_type = st.selectbox("Choose your input type", ['slider', 'text'], index=['slider', 'text'].index(st.session_state['input_type']), key='input_type')

        # if input_type == 'slider':
        #     min_danger, max_danger = st.slider("🚨 Select a range of danger", 0.0, 100.0, 
        #                                     (st.session_state['min_danger'], st.session_state['max_danger']), 
        #                                     key='danger_range_slider')
        #     st.session_state['min_danger'] = min_danger
        #     st.session_state['max_danger'] = max_danger
        # else:
        col1, col2, col3 = st.columns([4.5,1,4.5])
        with col1:
            st.session_state['min_danger'] = st.number_input("🚨 Enter minimum danger : ", min_value = 0.0, max_value=100.0, 
                                                        value=st.session_state['min_danger'], key='min_danger_input')
        with col2:
            st.write("\n")
            st.markdown("**<center>~</center>**", unsafe_allow_html=True)
        with col3:
            st.session_state['max_danger'] = st.number_input("🚨 Enter maximum danger : ", min_value = 0.0, max_value=100.0, 
                                                        value=st.session_state['max_danger'], key='max_danger_input')


        if st.button('OK'):
            list_accommodation_id = danger_api.get_danger(st.session_state['min_danger'],st.session_state['max_danger'],to_list=True)
            if not list_accommodation_id:
                st.write("해당 범위에는 숙소가 존재하지 않습니다.")
            else:
                st.session_state['list_accommodation_id'] = list_accommodation_id
                st.session_state['accommodation_id'] = None
                switch_page('Listpage')



if selected=='Airbnb Info':
    switch_page('Listpage')

if selected=='Team':
    switch_page('Team')
