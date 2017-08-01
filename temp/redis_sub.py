# coding=utf-8  
''''' 
Created on 2015-9-9 

@author: kwsy 
'''
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe('user')
for item in p.listen():
    print(item)
    if item['type'] == 'message':
        data = item['data']
        print(data)
        if item['data'] == 'over':
            break;
p.unsubscribe('user')
