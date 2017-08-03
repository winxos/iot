# coding=utf-8
'''''
Created on 2015-9-9

@author: Administrator
'''
import redis

r = redis.Redis(host='localhost', db=1)
while True:
    s = input("publish:")
    if s == 'over':
        print('停止发布')
        break;
    r.publish('user', s)
