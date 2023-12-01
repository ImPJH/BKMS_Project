import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pandas as pd
import util.postgresql_helper as postgresql_helper
import streamlit as st
import psycopg2
from pandas.io import gbq
import pydata_google_auth

def get_price(min_price: int, max_price : int, to_list=False):
    sql = f'SELECT id FROM accommodation WHERE price >={min_price} and price <={max_price} ORDER BY price ASC LIMIT 5'
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list: return data['id'].values.tolist()
    else: return data