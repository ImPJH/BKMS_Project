#왼쪽에 지도 띄우고 검색한 숙소 핀 찍고 위험도별 색깔 칠하고 -현빈언니's
#오른쪽에 검색한 숙소 리스트 띄우고 -지형오빠's

#특정 숙소를 클릭하면 아래쪽에 숙소 정보 관련 정보 띄우고 주변 범죄 관련 정보도 띄우고 -서노나으니

import search
import apis.display as display
import pandas as pd
import streamlit as st

#클릭한 숙소 id를 가져오기

id = 3539882
acc = display.accommodation_info(id)#가져온 id 넣어주기
#'name' ('room_type', 'price')
#host 관련 정보 : 'host_name', 'host_is_superhost'
#room 관련 정보 : 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'amenities', 'minimum_nights', 'maximum_nights'
#review 관련 정보 : 'review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location'
st.header(acc.name[0]+ " ("+ acc.room_type[0]+ " , " + str(acc.price[0]) + " $)")

st.subheader('Host 관련 정보')

if acc.host_is_superhost[0] == True:
    st.markdown(f":first_place_medal: {acc.host_name[0]}") 
else:
    st.markdown(acc.host_name[0])


df3 = pd.DataFrame(acc[['host_name', 'host_is_superhost']], 
                   columns = ('host_name', 'host_is_superhost'))

st.subheader('Room 관련 정보')
df1 = pd.DataFrame(acc[['accommodates', 'bathrooms', 'bedrooms', 'beds','minimum_nights', 'maximum_nights']], 
                   columns = ['accommodates', 'bathrooms', 'bedrooms', 'beds','minimum_nights', 'maximum_nights'])
df1.rename(index={0:'num'}, inplace=True)
st.table(df1)


st.subheader('Amenity 관련 정보')
acc1=acc.amenities.values
st.markdown(acc1[0])


st.subheader('Review 관련 정보')
df2 = pd.DataFrame(acc[['review_num', 'review_avg', 'review_cleanliness', 'review_checkin', 'review_location']])
df2 = df2.astype('float')

review_num = int(acc['review_num'][0])
review_avg = round(acc['review_avg'][0], 2)
review_cleanliness = round(acc['review_cleanliness'][0], 2)
review_checkin = round(acc['review_checkin'][0], 2)
review_location= round(acc['review_location'][0], 2)

if review_avg<=1.5:
    st.markdown("⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
elif review_avg<=2.5:
    st.markdown("⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
elif review_avg<=3.5:
    st.markdown("⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
elif review_avg<=4.5:
    st.markdown("⭐⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")
else:
    st.markdown("⭐⭐⭐⭐⭐ ("+str(review_avg)+", "+str(review_num)+" Reviews)")

st.write('Review Cleanliness: '+str(review_cleanliness)+"/5")
st.write('Review Check-in: '+str(review_checkin)+"/5")
st.write('Review Location: '+str(review_location)+"/5")