#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 14:05:09 2020

@author: ShihaoYang
"""

import re # 正则表达式库
import jieba   #分词
import collections # 词频统计库
import numpy as np
import pandas as pd
import networkx as nx  #复杂网络分析库
import matplotlib.pyplot as plt
import jieba.posseg as pseg

num=50
G=nx.Graph()
plt.figure(figsize=(200,160))
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
#plt.rcParams['font.sans-serif'] = ['SimHei']   # 用来正常显示中文标签

import os

os.listdir()
# 读取文件
fn = open('/users/emilywang/shihao yang/beef.txt') # 打开文件
string_data = fn.read() # 读出整个文件
fn.close() # 关闭文件

# 文本预处理
pattern = re.compile(u'\t|\.|-|:|;|\)|\(|\?|"') # 定义正则表达式匹配模式
string_data = re.sub(pattern, '', string_data) # 将符合模式的字符去除

#添加词库
exfood = open('/users/emilywang/shihao yang/food.txt').read().split('\n') # 自定义词库
exbody = open('/users/emilywang/shihao yang/body.txt').read().split('\n') # 自定义词库
exmedi = open('/users/emilywang/shihao yang/medical.txt').read().split('\n') # 自定义词库
exnutri = open('/users/emilywang/shihao yang/nutrition.txt').read().split('\n') # 自定义词库

eximportant = ['有效','增强','补充','增长','增加','促进','含有','有助于','有利于','好处','支持','产生','作用','抑制','富含','保持','提高','必需','供给']



total = exfood + exbody + exmedi + exnutri
total.remove('口服')
total.remove('抑制')
# 文本分词
jieba.add_word('维生素B6')
jieba.add_word('维生素B1')
jieba.add_word('维生素B12')
jieba.add_word('丙胺酸')
jieba.add_word('头几秒钟')
jieba.load_userdict('/users/emilywang/shihao yang/food.txt')
jieba.load_userdict('/users/emilywang/shihao yang/body.txt')
jieba.load_userdict('/users/emilywang/shihao yang/medical.txt')
jieba.load_userdict('/users/emilywang/shihao yang/nutrition.txt')


seg_list_exact = jieba.cut(string_data, cut_all = False) # 精确模式分词
object_list = []
remove_words = open('/users/emilywang/shihao yang/stopword.txt').read().split('\n') # 自定义去除词库
remove_words.append("\n")
#print(remove_words)

for word in seg_list_exact: # 循环读出每个分词
    if word not in remove_words: # 如果不在去除词库
        if word in total:
            object_list.append(word) # 分词追加到列表

        # 词频统计
word_counts = collections.Counter(object_list) # 对分词做词频统计
word_counts_top = word_counts.most_common(len(word_counts)) # 获取最高频的词
word = pd.DataFrame(word_counts_top, columns=['关键词','次数'])
#print(word)
num = len(word_counts)
word_T = pd.DataFrame(word.values.T,columns=word.iloc[:,0])
net = pd.DataFrame(np.mat(np.zeros((num,num))),columns=word.iloc[:,0])

k = 0
#构建语义关联矩阵
line = []
for i in range(len(string_data)):
    if string_data[i] in ['\n','。']:  #根据换行符读取一段文字
        seg = list(jieba.cut(string_data[k:i], cut_all = False)) # 精确模式分词
        object_list2 = []
        flag = 0
        mainword = ""
        for j in range(len(seg)): # 循环读出每个分词
            if flag == 0 and seg[j] in total and seg[j] != '':
                mainword = seg[j]
                flag = 1
                continue
            if flag ==1 and seg[j] in eximportant:
                for k in range(1,4):
                    if j+k < len(seg) and seg[j+k] != mainword and seg[j+k] in total:
                        line.append([mainword,seg[j+k],seg[j]])
                    if j-k >= 0 and seg[j-k] != mainword and seg[j-k] in total:
                        line.append([mainword,seg[j-k],seg[j]])
        k = i + 1
'''
n = len(word)
        # 边的起点，终点，权重
for i in range(n):
    for j in range(i, n):
        G.add_weighted_edges_from([(word.iloc[i, 0], word.iloc[j, 0], net.iloc[i, j])])
#print(G.edges())
nx.draw_networkx(G,
                    pos=nx.spring_layout(G),
                    # 根据权重的大小，设置线的粗细
                    width=[float(v['weight'] / 5) for (r, c, v) in G.edges(data=True)],
                    edge_color='orange',
                    # 根据词出现的次数，设置点的大小
                    node_size=[float(net.iloc[i, i] * 6) for i in np.arange(15)],node_color='white'
                    )

#plt.title('助攻表现（常规赛）',fontstyle='oblique')
plt.savefig('out3.23(5).png')
plt.show()
'''
