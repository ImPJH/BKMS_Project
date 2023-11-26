import streamlit as st
import bcrypt
import psycopg2
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import apis.display as display_api
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
            st.metric('Username', f'👤 {user_name}')
            col1, col2, _, _ = st.columns(4)
            col1.metric('Age', user_age)
            col2.metric('Gender', user_gender)
            st.divider()

            if st.button('Update Information'):
                st.session_state.page = 'update_info'
                switch_page('login')

            col1, col2, _, _, _, _, _, _, _, _ = st.columns(10)
            if col2.button('Main'):
                switch_page('Main')

            if col1.button('Logout'):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.page = 'login'
                switch_page('login')

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
app()