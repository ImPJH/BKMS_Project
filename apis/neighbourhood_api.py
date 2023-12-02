import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pandas as pd
import util.postgresql_helper as postgresql_helper

# to_list를 True로 할 시 python list형태로 출력, default는 False이며 False인 경우 pandas dataframe으로 출력

# neighbourhood_group list 보여줄 때 사용
def get_distinct_neighbourhood_group(to_list=False):
    sql = 'select distinct neighbourhood_group from neighbourhood ORDER BY neighbourhood_group ASC'
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list: return data['neighbourhood_group'].values.tolist()
    else: return data

# neighbourhood_group 선택 후 해당하는 neighbourhood들을 보여줄 때 사용
def get_neighbourhood_in_neighbourhood_group(neighbourhood_group: str, to_list=False):
    sql = f"SELECT neighbourhood FROM neighbourhood WHERE neighbourhood_group = '{neighbourhood_group}' ORDER BY neighbourhood ASC"
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list : return data['neighbourhood'].values.tolist()
    else: return data

# neighbourhood id를 받아와서 accommodation id들을 리턴하는 함수
def get_accommodation_id_by_neighbourhoods(neighbourhood:str,neighbourhood_group: str,min_price=None, max_price=None, to_list=False):
    sql = f"SELECT neighbourhood_id FROM neighbourhood WHERE (neighbourhood = '{neighbourhood}' and neighbourhood_group = '{neighbourhood_group}')"
    sql_type = 'select'
    neighbourhood_id = postgresql_helper.run(sql,sql_type)['neighbourhood_id'][0]

    if (min_price is None) and (max_price is None):
        sql = f"SELECT id FROM accommodation WHERE neighbourhood_id = {neighbourhood_id} ORDER BY airbnb_danger_normalized ASC"
    else:
        sql = f"SELECT id FROM accommodation WHERE (neighbourhood_id = {neighbourhood_id} AND price >= {min_price} AND price <= {max_price}) ORDER BY airbnb_danger_normalized ASC"
    sql_type = 'select'
    data = postgresql_helper.run(sql,sql_type)
    if to_list : return data['id'].values.tolist()
    else: return data
