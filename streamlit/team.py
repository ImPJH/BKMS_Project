import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import json

st.set_page_config(
    page_title="TEAM",
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

#Options Menu
with st.sidebar:
    selected = option_menu('BSAFE', ["Main", 'Search','Team'],
        icons=['house','search','people'],menu_icon='airplane', default_index=2)
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
        col1.write('Contribution : Construct DB')
        col2.image('./photo/sr.png', width = 300)
        image_url = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
        github_url = "https://github.com/Seorin-Kim"
        logo_url = 'https://icons.veryicon.com/png/o/food--drinks/pakd/mail-218.png'
        email = 'seorin1116@snu.ac.kr'
        col1.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<a href="{github_url}" target="_blank" style="margin-right: 10px;"><img src="{image_url}" alt="Repo" width="25"/></a>'
            f'<a href="mailto:{email}"><img src="{logo_url}" alt="Email" width="26"/></a>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.divider()

    with st.container():
        col1,col2=st.columns(2)
        col1.image('./photo/sh.png', width = 270)
        col2.write('')
        col2.subheader('박선호')
        col2.write('M.S. Student @ SNU GSDS')
        col2.write('Contribution : Frontend')
        image_url = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
        github_url = "https://github.com/preferpark99"
        logo_url = 'https://icons.veryicon.com/png/o/food--drinks/pakd/mail-218.png'
        email = 'preferpark99@snu.ac.kr'
        col2.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<a href="{github_url}" target="_blank" style="margin-right: 10px;"><img src="{image_url}" alt="Repo" width="25"/></a>'
            f'<a href="mailto:{email}"><img src="{logo_url}" alt="Email" width="26"/></a>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.divider()
    with st.container():
        col1,col2=st.columns(2)
        col1.write('')
        col1.subheader('박지형')
        col1.write('M.S. Student @ SNU GSDS')
        col1.write('Contribution : Backend')
        col2.image('./photo/jh.png', width = 300)
        image_url = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
        github_url = "https://github.com/ImPJH"
        logo_url = 'https://icons.veryicon.com/png/o/food--drinks/pakd/mail-218.png'
        email = 'impjhy1129@snu.ac.kr'
        col1.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<a href="{github_url}" target="_blank" style="margin-right: 10px;"><img src="{image_url}" alt="Repo" width="25"/></a>'
            f'<a href="mailto:{email}"><img src="{logo_url}" alt="Email" width="26"/></a>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.divider()

    with st.container():
        col1,col2=st.columns(2)
        col1.image('./photo/ne.png', width = 270)
        col2.write('')
        col2.subheader('이나은')
        col2.write('M.S. Student @ SNU GSDS')
        col2.write('Contribution : Backend')
        image_url = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
        github_url = "https://github.com/better62"
        logo_url = 'https://icons.veryicon.com/png/o/food--drinks/pakd/mail-218.png'
        email = 'better__62@snu.ac.kr'
        col2.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<a href="{github_url}" target="_blank" style="margin-right: 10px;"><img src="{image_url}" alt="Repo" width="25"/></a>'
            f'<a href="mailto:{email}"><img src="{logo_url}" alt="Email" width="26"/></a>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.divider()
    with st.container():
        col1,col2=st.columns(2)
        col1.write('')
        col1.subheader('진현빈')
        col1.write('M.S. Student @ SNU GSDS')
        col1.write('Contribution : Frontend')
        col2.image('./photo/hb.png', width = 300)
        image_url = "https://cdn-icons-png.flaticon.com/512/25/25231.png"
        github_url = "https://github.com/hyunbinui"
        logo_url = 'https://icons.veryicon.com/png/o/food--drinks/pakd/mail-218.png'
        email = 'hyunbin.jin@snu.ac.kr'
        col1.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<a href="{github_url}" target="_blank" style="margin-right: 10px;"><img src="{image_url}" alt="Repo" width="25"/></a>'
            f'<a href="mailto:{email}"><img src="{logo_url}" alt="Email" width="26"/></a>'
            f'</div>',
            unsafe_allow_html=True
        )            


