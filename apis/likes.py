import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from util.postgresql_helper import run

# for like button

def find_like(username, airbnb_id):
    # 있는지 확인해서 있으면 cnt를 반환하고 없으면 0을 반환하기
    sql = f"SELECT user_id, airbnb_id, cnt FROM likes WHERE user_id = '{username}' AND airbnb_id = {airbnb_id}"
    likes_table = run(sql, 'select')
    
    if len(likes_table) != 0:
        return likes_table.loc[0, 'cnt']
    else:
        return 0

def first_like(username, airbnb_id):
    sql = f"INSERT INTO likes (user_id, airbnb_id, cnt) VALUES ('{username}', {airbnb_id}, 1)"
    run(sql, 'insert')

def click_like(username, airbnb_id, cnt):
    sql = f"UPDATE likes SET cnt = {cnt} WHERE user_id = '{username}' AND airbnb_id = {airbnb_id}"
    run(sql, 'update')



# like list
def like_list(username):
    sql = f"SELECT airbnb_id FROM likes WHERE user_id = '{username}' AND cnt%2 = 1"
    likes_table = run(sql, 'select')
    return likes_table['airbnb_id'].values.tolist()