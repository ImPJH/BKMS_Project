import streamlit as st
import bcrypt
import psycopg2
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page
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

    if st.button("Log in"):
        if check_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.warning("Incorrect username or password")


# 회원가입 페이지를 보여주는 함수
def show_signup():
    st.title("Sign up")
    new_username = st.text_input("New username")
    new_password = st.text_input("New password", type="password")
    new_age = st.number_input("Your age", min_value=0, max_value=120)  # 나이 입력
    new_gender = st.selectbox("Your gender", options=["Male", "Female", "Other"])  # 성별 선택


    if st.button("Sign up"):
        if check_user(new_username, new_password): 
            st.warning("This username is already taken")
        else:
            add_user(new_username, new_password, new_age, new_gender)  # add_user 함수를 호출하여 사용자 정보를 데이터베이스에 저장
            st.success("You have successfully signed up")

# 메인 함수
def app():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        switch_page('Main')
    else:
        if st.session_state.page == "login":
            show_login()
            if st.button("Click here to sign up"):
                st.session_state.page = "signup"
        elif st.session_state.page == "signup":
            show_signup()
            if st.button("Click here to log in"):
                st.session_state.page = "login"

app()