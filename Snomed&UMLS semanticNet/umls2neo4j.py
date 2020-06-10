#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 09:43:34 2020

@author: emilywang
"""

import os
from py2neo import Graph,Node
import pandas as pd
import re
from pymongo import MongoClient

g = Graph(
    host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=7687,  # neo4j 服务器监听的端口号
    user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
    password="wdygcs")

client = MongoClient(host="localhost", port=27017)
db = client.get_database("umls_all3")
concept = db.concept

conceptnode = concept.find({},{ "_id": 1,"one_of_name" : 1,"definition":1,"semtype":1})
conceptnode = list(conceptnode)
for i in range(len(conceptnode)):
    row = conceptnode[i]
    if "definition" not in row:
        tempnode = Node('&'.join(row["semtype"]),name = row["_id"],oneofname = row["one_of_name"])
    else:
        tempnode = Node('&'.join(row["semtype"]),name = row["_id"],definition=('|'.join(row["definition"])),oneofname = row["one_of_name"])
    g.create(tempnode)
    if i%10000==0:
        print(i)
del(conceptnode)

checkconcept = list(concept.find({},{ "_id": 1}))
checkconcept = list(map(lambda x: x["_id"],checkconcept))

def create_relationship(checkconcept):
    count = 0
    conceptnode = concept.find({},{ "_id": 1,"rel": 1})
    conceptnode = list(conceptnode)
    try:
        for i in range(len(conceptnode)):
            row = conceptnode[i]
            if "rel" not in row:
                pass
            else:
                try:
                    for key in row["rel"].keys():
                        if key not in ['other','synonym','related','child','sibling','narrower','broader','parent']:
                            for n in row["rel"][key]:
                                if n != row["_id"]:
                                    p = row["_id"]
                                    q = n
                                    query = 'match(p),(q) where p.name="%s"and q.name="%s" create (p)-[r:%s{name:"%s"}]->(q)' % (p, q, key, key)
                                    #try:
                                    g.run(query)
                                    count += 1
                                    if count%10000 ==0:
                                        print(count)
                except:
                    print("out")
            if i%1000 == 0:
                print('i:',i)
    except:
        print('error!')
    return

#####i 
create_relationship(checkconcept)