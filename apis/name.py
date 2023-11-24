import streamlit as st
import psycopg2
import pandas as pd
from pandas.io import gbq

import pydata_google_auth

# BigQuery 연결하기

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/bigquery'
]

credentials = pydata_google_auth.get_user_credentials(
  SCOPES, auth_local_webserver=False)


# DBeaver 연결하기
connection_info = "host=147.47.200.145 dbname=teamdb5 user=team5 password=newyork port=34543"
conn = psycopg2.connect(connection_info)
cur=conn.cursor()


def clustering(precinct, id):
    table = "airbnb."+str(precinct)
    sql = "SELECT * FROM "+table
    project_id = "airbnb-405907"
    clustering_df = pd.read_gbq(sql, project_id=project_id, credentials=credentials, dialect='standard')
    centroid = clustering_df[clustering_df['id']==id]['CENTROID_ID'].values
    id_list = clustering_df[clustering_df['CENTROID_ID']==centroid[0]]['id'].tolist()

    return id_list
    

 

# 이름 검색 구현
def search_from_name():

    # 테이블 불러오기
    query = "select * from accommodation"
    cur.execute(query)

    accomodation = pd.read_sql(query, conn)

    name_list = accomodation['name'].to_list()

    fname = st.text_input('숙소 이름을 입력하세요.')

    if fname in name_list:
        neighbourhood_id = list(accomodation[accomodation['name']==fname]['neighbourhood_id'])
        query = "select precinct from neighbourhood where neighbourhood_id="+str(neighbourhood_id[0])
        precinct_df = pd.read_sql(query, conn)
        precinct = list(precinct_df['precinct'])[0]
        id = list(accomodation[accomodation['name']==fname]['id'])
        candidate = clustering(precinct, id[0])
        sorted_candidate = accomodation[accomodation['id'].isin(candidate)].sort_values(by='airbnb_danger_normalized',ascending=False)
        return sorted_candidate['id'].tolist()
    else:
        return None
    

search_from_name()
conn.close()