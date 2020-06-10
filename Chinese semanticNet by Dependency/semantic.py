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
num=15
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
exvege = open('/users/emilywang/shihao yang/vegetable.txt').read().split('\n') # 自定义词库
exele = ['钾','钙','纳','镁','锌','铁','汞']
eximportant = ['有效','增强','补充','增长','增加','促进','含有','有助于','有利于','好处','低','高','支持','产生','作用','抑制','富含','保持','提高','必须','供给']
total = exfood + exbody + exmedi + exnutri + exvege + exele + eximportant

# 文本分词
jieba.add_word('维生素B6')
jieba.add_word('维生素B1')
jieba.add_word('丙胺酸')
jieba.load_userdict("food.txt")
jieba.load_userdict("body.txt")
jieba.load_userdict("medical.txt")
jieba.load_userdict("nutrition.txt")
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
word_counts_top = word_counts.most_common(num) # 获取最高频的词
word = pd.DataFrame(word_counts_top, columns=['关键词','次数'])
#print(word)

word_T = pd.DataFrame(word.values.T,columns=word.iloc[:,0])
net = pd.DataFrame(np.mat(np.zeros((num,num))),columns=word.iloc[:,0])

k = 0
#构建语义关联矩阵
for i in range(len(string_data)):
    if string_data[i] in ['\n','。']:  #根据换行符读取一段文字
        seg_list_exact = jieba.cut(string_data[k:i], cut_all = False) # 精确模式分词
        object_list2 = []
        for words in seg_list_exact: # 循环读出每个分词
            if words not in remove_words and words in total: # 如果不在去除词库中
                object_list2.append(words) # 分词追加到列表
                
        if object_list2 ==[]:
            continue
        word_counts2 = collections.Counter(object_list2)
        word_counts_top2 = word_counts2.most_common(num) # 获取该段最高频的词
        word2 = pd.DataFrame(word_counts_top2)
        word2_T = pd.DataFrame(word2.values.T,columns=word2.iloc[:,0])
        relation = list(0 for x in range(num))
        # 查看该段最高频的词是否在总的最高频的词列表中
        for j in range(num):
            for p in range(len(word2)):
                if word.iloc[j,0] == word2.iloc[p,0]:
                    relation[j] = 1
                    break
        #对于同段落内出现的最高频词，根据其出现次数加到语义关联矩阵的相应位置
        for j in range(num-1):
            if relation[j] == 1:
                for q in range(j+1,num):
                    if relation[q] == 1:
                        net.iloc[j, q] = net.iloc[j, q] + 1
            k = i + 1

            # 处理最后一段内容，完成语义关联矩阵的构建


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

