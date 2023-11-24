import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import json

hide_pages(['login', 'Main', 'Team','Search'])

show_pages([
    Page("page.py","Main"),
    Page("login.py","login"),
    Page("team.py","Team"),
    Page("search.py","Search")
])


@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

#Options Menu
with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search','Team'],
        icons=['house','search','info-circle'],menu_icon='intersect', default_index=2)
    lottie = load_lottiefile("similo3.json")
    st_lottie(lottie,key='loc')


if selected == "Main":
    switch_page('Main')

if selected == "Search":
    switch_page("Search")

if selected == "Team":  
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
