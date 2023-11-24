import streamlit as st

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
