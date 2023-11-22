# 빈번히 사용할 모듈 모음  
## postgresql_helper.py 사용법  
> postgresql에 sql을 날리고 싶은 경우 사용.  
> run(sql,sql_type,connection_info="host=147.47.200.145 dbname=teamdb5 user=team5 password=newyork port=34543")  
> sql: sql문을 입력  
> sql_type: ('select' or 'update')만 가능 sql문이 select문인 경우 'select', update 문인 경우 'update'  
> Lecture18.ipynb의 예제 그대로 사용함  
```python
from postgresql import run
sql = 'SELECT neighbourhood.precinct_danger FROM neighbourhood WHERE neighbourhood_id = 51;'  
sql_type = 'select'  
run(sql,sql_type)  
```
> sql_type이 'select'인 경우 결과 dataframe이 출력됨. 'update'인 경우 아무것도 출력 안함.  
> scheduling을 하고 싶은 경우 사용하지 말 것