import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pandas as pd
import util.postgresql_helper as postgresql_helper
import streamlit as st
import psycopg2
from pandas.io import gbq
import pydata_google_auth

def get_price(min_price: int, max_price : int, order_by:str, to_list=False):
    if order_by == 'Danger':
        sql = f'''
        SELECT a.id 
        FROM accommodation a
        JOIN neighbourhood n ON a.neighbourhood_id = n.neighbourhood_id 
        WHERE a.price >= {min_price} AND a.price <= {max_price} 
        ORDER BY ((n.precinct_danger_normalized*1000 + a.airbnb_danger_normalized*100000)/2) ASC
        LIMIT 5
        '''
    else:
        sql = f"SELECT id FROM accommodation WHERE price >= {min_price} AND price <= {max_price} ORDER BY price ASC LIMIT 5"
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list: return data['id'].values.tolist()
    else: return data