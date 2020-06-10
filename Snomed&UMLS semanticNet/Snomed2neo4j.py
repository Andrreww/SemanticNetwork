#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:38:28 2020

@author: ShihaoYang
"""

import os
from py2neo import Graph,Node
import pandas as pd
import re
cur_dir = r'/Users/emilywang/shihao yang'   # 获取当前绝对路径的上层目录 linux中应用'/'split和join
data_path = os.path.join(cur_dir, 'snomed.csv')   # 获取json文件路径
g = Graph(
    host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    http_port=7687,  # neo4j 服务器监听的端口号
    user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
    password="wdygcs")

def typefind(s):
    p1 = re.compile(r'[(](.*?)[)]', re.S)
    return re.findall(p1, s)[-1]

def withouttypefind(s):
    return s[:-len(typefind(s))-2].strip()

data = pd.read_csv(data_path)
data.fillna('0',inplace = True)
data['type'].unique()
rels = data.columns[5:]
conceptclass  = {}
for i in data['type'].unique():
    conceptclass[i] = []
relation = {}
for i in rels:
    relation[i] = [] 
relation_syn = []
for _, row in data.iterrows():
    conceptclass[row['type']].append(row['name'])
    for i in row['SYNONYM'].strip().split('|'):
        conceptclass[row['type']].append(i)
        relation_syn.append([row['name'],i])
        relation_syn.append([i,row['name']])
    for i in rels:
        if row[i] != '0':
            for j in row[i].strip().split('|'):
                relation[i].append([row['name'],withouttypefind(j)])
                if typefind(j) not in conceptclass:
                    conceptclass[typefind(j)] = []
                conceptclass[typefind(j)].append(withouttypefind(j))
#create node
for key in conceptclass:
    conceptclass[key] = list(set(conceptclass[key]))

count = 0
for key in conceptclass:
    for n in conceptclass[key]:
        node = Node(key, name=n)
        g.create(node)
        count += 1
    
def create_relationship(edges, rel_type):
    count = 0
    # 去重处理
    set_edges = []
    for edge in edges:
        set_edges.append('###'.join(edge))
    for edge in list(set(set_edges)):
        edge = edge.split('###')
        p = edge[0]
        q = edge[1]
        query = 'match(p),(q) where p.name="%s"and q.name="%s" create (p)-[r:%s{name:"%s"}]->(q)' % (p, q, rel_type, rel_type)
        #try:
        print(query)
        g.run(query)
        count += 1
    return
      
create_relationship(relation_syn,'SYNONYM') 
for key in relation.keys():
    create_relationship(relation[key],re.sub(' ','_',withouttypefind(key))) 
    print(key)
        
        
        
        