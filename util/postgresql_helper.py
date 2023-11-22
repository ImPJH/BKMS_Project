# psycopg2 import
import psycopg2
import pandas as pd

def run(sql,sql_type,connection_info="host=147.47.200.145 dbname=teamdb5 user=team5 password=newyork port=34543"
):
    if type(sql) != str: raise Exception('sql문은 string이어야 합니다.')
    if sql_type not in ['select','update']: raise Exception("sql_type은 'select'거나 'update'여야 합니다.")

    conn = psycopg2.connect(connection_info)
    if sql_type == 'select':
        reaction = None
        try:
            reaction = pd.read_sql(sql,conn)

        except psycopg2.Error as e:
            print("DB error: ", e)

        finally:
            conn.close()
    
        return reaction
    
    elif sql_type == 'update':
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

        except psycopg2.Error as e:
            print("DB error: ", e)
            conn.rollback()

        finally:
            conn.close()
