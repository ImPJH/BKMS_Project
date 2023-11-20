import yaml
from yaml.loader import SafeLoader
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth



### 사용자 정보 yaml 파일로 저장

names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]
passwords = ["abc123", "def456"]

hashed_passwords = stauth.Hasher(passwords).generate()

# 위의 names, usernames, hashed_passwords 합쳐서 config.yaml 형식으로 묶어서 저장해야 함
file_path = Path(__file__).parent / "my_config.yaml"
with file_path.open("w") as file:
    yaml.dump(hashed_passwords, file)



### 사용자 정보 불러오기
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)



### 로그인
authenticator.login("Login", "main")

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')



### 비밀번호 변경
if st.session_state["authentication_status"]:
    try:
        if authenticator.reset_password(st.session_state["username"], 'Reset password'):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)



### 회원가입
try:
    if authenticator.register_user('Register user', preauthorization=False):
        st.success('User registered successfully')
except Exception as e:
    st.error(e)



### 비밀번호 잊어버렸을 때
try:
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password('Forgot password')
    if username_of_forgotten_password:
        st.success('New password to be sent securely')
        # Random password should be transferred to user securely
    else:
        st.error('Username not found')
except Exception as e:
    st.error(e)



### 아이디 잊어버렸을 때 
try:
    username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username('Forgot username')
    if username_of_forgotten_username:
        st.success('Username to be sent securely')
        # Username should be transferred to user securely
    else:
        st.error('Email not found')
except Exception as e:
    st.error(e)



### 사용자 정보 변경
if st.session_state["authentication_status"]:
    try:
        if authenticator.update_user_details(st.session_state["username"], 'Update user details'):
            st.success('Entries updated successfully')
    except Exception as e:
        st.error(e)



### 사용자 정보 파일(config.yaml) 업데이트
with open('../config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)