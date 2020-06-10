#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 09:33:02 2020

@author: ShihaoYang
"""
import os
from py2neo import Graph,Node
import pandas as pd
import re
from pymongo import MongoClient


os.chdir('/Users/emilywang/shihao yang')
conceptlist = pd.read_csv('conceptlist.csv',header = None)
conceptlist = list(conceptlist.iloc[:,0])

g = Graph(
    host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=7687,  # neo4j 服务器监听的端口号
    user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
    password="wdygcs")

client = MongoClient(host="localhost", port=27017)
db = client.get_database("umls_all2")
string = db.string
concept = db.concept

totalconcept = []
for i in range(len(conceptlist)):
    filter = {}
    keyword = conceptlist[i].lower()
    condition = {}
    condition['$regex'] = keyword
    filter["lower"] = condition
    conceptdict = list(string.find(filter,{"string" : 1,"cui" : 1}))
    for c in conceptdict:
        if list(concept.find({'_id':c['cui']})) != 0 and c['cui'] not in totalconcept:
            totalconcept.append(c['cui'])
            
totalconcept = list(set(totalconcept))

conceptnode = concept.find({"_id":{"$in":totalconcept}},{ "_id": 1,"one_of_name" : 1,"definition":1,"semtype":1})
conceptnode = list(conceptnode)
for i in range(len(conceptnode)):
    row = conceptnode[i]
    if "definition" not in row:
        tempnode = Node('&'.join(row["semtype"]),name = row["_id"],oneofname = row["one_of_name"])
    else:
        tempnode = Node('&'.join(row["semtype"]),name = row["_id"],definition=('|'.join(row["definition"])),oneofname = row["one_of_name"])
    g.create(tempnode)
    if i%1000==0:
        print(i)
del(conceptnode)

def create_relationship(totalconcept):
    count = 0
    conceptnode = concept.find({"_id":{"$in":totalconcept}},{ "_id": 1,"rel": 1})
    conceptnode = list(conceptnode)
    for i in range(len(conceptnode)):
        row = conceptnode[i]
        try:
            for key in row["rel"].keys():
                if key not in ['other','synonym','related','child','sibling','narrower']:
                    for n in row["rel"][key]:
                        if n not in totalconcept:
                            continue
                        p = row["_id"]
                        q = n
                        query = 'match(p),(q) where p.name="%s"and q.name="%s" create (p)-[r:%s{name:"%s"}]->(q)' % (p, q, key, key)
                        #try:
                        g.run(query)
                        count += 1
                        if count%100 ==0:
                            print(count)
        except:
            print('error!')
        if i%100 == 0:
            print('i:',i)

    return
create_relationship(totalconcept)