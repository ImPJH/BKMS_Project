import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import pandas as pd
import util.postgresql_helper as postgresql_helper
import streamlit as st
import psycopg2
from pandas.io import gbq
import pydata_google_auth
from util.postgresql_helper import run

def get_danger(min_danger: float, max_danger : float, to_list=False):
    sql = f'''
    SELECT a.id 
    FROM accommodation a
    JOIN neighbourhood n ON a.neighbourhood_id = n.neighbourhood_id 
    WHERE ((n.precinct_danger_normalized*1000 + a.airbnb_danger_normalized*100000)/2) >= {min_danger} 
    AND ((n.precinct_danger_normalized*1000 + a.airbnb_danger_normalized*100000)/2) <= {max_danger} 
    ORDER BY ((n.precinct_danger_normalized*1000 + a.airbnb_danger_normalized*100000)/2) ASC
    LIMIT 5
    '''
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list: return data['id'].values.tolist()
    else: return data