import streamlit as st
import bcrypt
import psycopg2
import pandas as pd
import folium
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.display as display_api
import apis.likes as likes
#클릭한 숙소 id를 가져오기


st.set_page_config(
    page_title="LOGIN",
    layout="wide",
    page_icon="🫂",
    initial_sidebar_state="expanded")

hide_pages(['Team'])

show_pages([
    Page("page.py","Main"),
    Page("login.py","login"),
    Page("team.py","Team")
])

def create_users_table():
    conn = psycopg2.connect(
        dbname="teamdb5",
        user="team5",
        password="newyork",
        host="147.47.200.145",
        port="34543"
    )
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users
        (username TEXT PRIMARY KEY, password TEXT, age INT, gender TEXT)
    ''')

    conn.commit()
    conn.close()

def add_user(username, password, age, gender):
    conn = psycopg2.connect(
        dbname="teamdb5",
        user="team5",
        password="newyork",
        host="147.47.200.145",
        port="34543"
    )
    c = conn.cursor()

    c.execute('''
        INSERT INTO users (username, password, age, gender) VALUES (%s, %s, %s, %s)
    ''', (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), age, gender))

    conn.commit()
    conn.close()

def check_user(username, password):
    conn = psycopg2.connect(
        dbname="teamdb5",
        user="team5",
        password="newyork",
        host="147.47.200.145",
        port="34543"
    )
    c = conn.cursor()

    c.execute('''
        SELECT password FROM users WHERE username = %s
    ''', (username, ))

    result = c.fetchone()
    conn.close()

    if result is None:
        return False

    return bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))

create_users_table()  # 앱이 시작될 때 사용자 테이블을 생성합니다.

# 사용자 정보를 저장하는 간단한 딕셔너리
users = {
    "pparker": bcrypt.hashpw("abc123".encode('utf-8'), bcrypt.gensalt()),
    "rmiller": bcrypt.hashpw("def456".encode('utf-8'), bcrypt.gensalt())
}

def check_password(username, password):
    if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]):
        return True
    return False

def main():
    st.title("Welcome to the main page!") #이 부분 이제 만든 페이지 갖다붙이면 될듯


# 로그인 페이지를 보여주는 함수
def show_login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            switch_page('Main')
        else:
            st.warning("Incorrect username or password")


# 회원가입 페이지를 보여주는 함수
def show_signup():
    st.title("Sign up")
    new_username = st.text_input("New username")
    new_password = st.text_input("New password", type="password")
    new_age = st.number_input("Your age", min_value=0, max_value=120)  # 나이 입력
    new_gender = st.selectbox("Your gender", options=["Male", "Female", "Others"])  # 성별 선택


    if st.button("Sign Up"):
        if new_username == '':
            st.warning("Enter the username")
        if new_password == '':
            st.warning("Enter the password")
        
        try:
            if check_user(new_username, new_password): 
                st.warning("This username is already taken")
            else:
                add_user(new_username, new_password, new_age, new_gender)  # add_user 함수를 호출하여 사용자 정보를 데이터베이스에 저장
                st.success("You have successfully signed up")
        except:
            st.warning("This username is already taken")


# 메인 함수
def app():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in and (st.session_state.page != 'mypage') and (st.session_state.page != 'update_info'):
        switch_page('Main')
    else:
        if st.session_state.page == "login":
            show_login()
            col1, col2, _, _, _, _, _, _, _, _ = st.columns(10)
            if col2.button('Main'):
                switch_page('Main')
            if col1.button("Sign Up"):
                st.session_state.page = "signup"
                switch_page('login')
        
        elif st.session_state.page == "signup":
            show_signup()
            col1, col2, _, _, _, _, _ = st.columns(7)
            if col2.button('Main'):
                st.session_state.page = "login"
                switch_page('Main')
            if col1.button("Back to Login"):
                st.session_state.page = "login"
                switch_page('login')
        
        elif st.session_state.page == 'mypage':
            user_name = st.session_state.username
            user_age, user_gender = display_api.user_info(user_name)

            st.title('My Page')
            st.divider()
            col1, _, _, _, _, _, col7, col8 = st.columns(8)
            if col1.button('Update Info'):
                st.session_state.page = 'update_info'
                switch_page('login')
            if col7.button('Logout'):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.page = 'login'
                switch_page('login')
            if col8.button('Main'):
                switch_page('Main')


            
            st.metric('Username', f'👤 {user_name}')
            col1, col2, _, col4 = st.columns(4)
            col1.metric('Age', user_age)
            col2.metric('Gender', user_gender)
            col4.write()


            st.divider()
            st.header('Liked Airbnb')

            liked = likes.like_list(st.session_state.username)
            col1, col2 = st.columns(2)

            with col2:
                accommodation_df = display_api.accommodations_simple_info(liked)
                st.markdown('''
                    <style>
                    .fullHeight {height : 80vh;
                        width : 100%}
                    </style>''', unsafe_allow_html = True)
                with st.container():
                    for idx, row in accommodation_df.iterrows():
                        # 버튼 내부 text 왼쪽정렬 -> CSS?
                        is_clicked = st.button(f"[danger: {round((row['precinct_danger_normalized']*1000+row['airbnb_danger_normalized']*100000)/2, 2)}] {row['name']}\n\n$ {row['price']} / {row['room_type']}", key = f"{row['id']}")
                        
                        if is_clicked: 
                            st.session_state['accommodation_id'] = row['id']

                if st.session_state['accommodation_id']:
                    id = st.session_state['accommodation_id']

            with st.container():
                if id:
                    m = make_map(id)
                    col1.write(m)

                else:
                    # id=None(지역검색인 경우) -> 첫번째 숙소로 지도 그리기
                    m = make_map(liked[0])
                    col1.write(m)


            if id:
                acc = display_api.accommodation_info(id)
                #'name' ('room_type', 'price')
                #host 관련 정보 : 'host_name', 'host_is_superhost'
                #room 관련 정보 : 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'amenities', 'minimum_nights', 'maximum_nights'
                #review 관련 정보 : 'review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location'
                
                st.divider()
                # if st.button('Back to Search'):
                #     switch_page('Search')
                
                if st.session_state.logged_in:
                    username = st.session_state.username
                    cnt = likes.find_like(username, id)

                    if cnt == 0:
                        if st.button('♡ Like'):
                            likes.first_like(username, id)
                            switch_page('login')
                    elif cnt % 2 == 0:
                        if st.button('♡ Like'):
                            likes.click_like(username, id, cnt+1)
                            switch_page('login')
                    elif cnt % 2 == 1:
                        if st.button('♥ Like'):
                            likes.click_like(username, id, cnt+1)
                            switch_page('login')
                
                else:
                    if st.button('♡ Like'):
                        st.warning("You need to login")
                        
                
                
                st.title(acc.name[0])

                col1, col2, col3 = st.columns(3)
                col1.metric('Price', str(acc.price[0]) + ' $')
                col2.metric('Room Type', acc.room_type[0])
                if acc.host_is_superhost[0] == True:
                    col3.metric('Host', f"{acc.host_name[0]} ✅")
                else:
                    col3.metric('Host', acc.host_name[0])

                tab1, tab2 = st.tabs(['Room Information', 'Reviews'])
                with tab1:
                    st.subheader('Room Information')
                    col1, col2, col3 = st.columns(3)
                    col1.metric('Accommodates', acc.accommodates[0])
                    col2.metric('Min Nights', acc.minimum_nights[0])
                    col3.metric('Max Nights', acc.maximum_nights[0])

                    st.divider()

                    st.subheader('Amenities')
                    col1, col2, col3 = st.columns(3)
                    col1.metric('Bathrooms', acc.bathrooms[0])
                    col2.metric('Bedrooms', acc.bedrooms[0])
                    col3.metric('Beds', acc.beds[0])


                    with st.expander('Amenities Details'):
                        amm = acc.amenities[0].replace('\n','').replace('\t','').split('|')
                        for a in amm:
                            st.write(a)

                with tab2:
                    st.subheader('Reviews')
                    col1, col2 = st.columns(2)
                    col1.metric('\#', int(acc.review_num[0]))
                    col2.metric('Average', str(acc.review_avg[0].round(2))+' '+'⭐'*int(acc.review_avg[0].round(0)))

                    col1, col2, col3 = st.columns(3)
                    col1.metric('Cleanliness', acc.review_cleanliness[0].round(2))
                    col2.metric('Check-in', acc.review_checkin[0].round(2))
                    col3.metric('Location', acc.review_location[0].round(2))
                    

                st.divider()

                st.title('Crime Information')

                neighbourhood_group, neighbourhood, precinct = display_api.neighbourhood_info(id)
                col1, col2, col3 = st.columns(3)
                col1.metric('Borough', neighbourhood_group)
                col2.metric('Neighbourhood', neighbourhood)
                col3.metric('Precinct', precinct)

                st.divider()

                tab1, tab2, tab3, tab4 = st.tabs(['Overall', 'Date', 'Crime Type', 'Victim'])
                with tab1:
                    display_api.crime_info(id, 'overall')
                with tab2:
                    display_api.crime_info(id, 'date')
                with tab3:
                    display_api.crime_info(id, 'crime_type')
                with tab4:
                    display_api.crime_info(id, 'victim')

        


        elif st.session_state.page == 'update_info':
            user_age, user_gender = display_api.user_info(st.session_state.username)
            new_age = st.number_input("Your age", min_value=0, max_value=120, value=user_age)  # 나이 입력
            new_gender = st.selectbox("Your gender", options=["Male", "Female", "Others"], index=["Male", "Female", "Others"].index(user_gender))  # 성별 선택

            col1, col2, _, _, _, _, _, _, _, _ = st.columns(10)
            if col1.button('Update'):
                try:
                    display_api.user_info_update(st.session_state.username, new_age, new_gender)
                except:
                    st.warning('Error in update')
                else:
                    st.success('You have successfully updated information')
            if col2.button('Main'):
                switch_page('Main')

def make_map(id):
    acc = display_api.accommodation_info(id)
    attraction = pd.read_csv('./data/merged_attraction.csv')
    heatmap = pd.read_csv('./data/precinct_danger_normalized.csv')

    geo_data = './data/neighbourhoods.geojson'
    latitude, longitude = acc['latitude'][0], acc['longitude'][0]
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

    la_guardia = [40.7900, -73.8700]
    jfk = [40.6650, -73.7821]
    newark = [40.7090, -74.1805]
    folium.Marker(location=la_guardia, 
                  tooltip='LaGuardia Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)
    folium.Marker(location=jfk, 
                  tooltip='JFK Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)
    folium.Marker(location=newark, 
                  tooltip='Newark Airport',
                  icon=folium.CustomIcon(icon_image='./photo/airport.png', icon_size=(37,37))).add_to(m)

    folium.Marker(
        location = [acc['latitude'][0], acc['longitude'][0]],
        tooltip = acc['name'][0],        # 마우스 갖다대면 나오는 문구
        popup = folium.Popup(f"{acc['description'][0]}", max_width=300, min_width=300),
        icon=folium.Icon(icon='heart',icon_color='white', color='red')
    ).add_to(m)

    return m





app()