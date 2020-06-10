#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 14:05:09 2020

@author: ShihaoYang
"""

import re # 正则表达式库
import collections # 词频统计库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import bs4 as bs
import urllib.request
import jieba
import jieba.posseg as pseg
import pattern3
from pattern3.graph import Graph
import webbrowser
from colorama import Fore, Style

os.getcwd()
os.chdir('/Users/emilywang/shihao yang')
os.getcwd()

def sent_tokenize_chinese(paragraph):
    for sentence in re.findall(u'[^!?。\!\?\？\！]+[!?。\!\?\？\！]?', paragraph, flags=re.U):
    # for sentence in re.findall(u'[^!?。\!\?\？\！\，]+[!?。\!\?\？\！\，]?', paragraph, flags=re.U):
        yield sentence


def word_tokenize_chinese(sentence):
    for sentence in re.findall(u'[^!?。\/\，\」\：\ \、]+[^!?。\/\，\」\：\ \、]?', sentence, flags=re.U):
        yield sentence

def print_error(error):
    print(Fore.RED)
    print('Exception Found:', error)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, f_name, exc_tb.tb_lineno)
    print(Style.RESET_ALL)
#添加词库
exfood = open('/users/emilywang/shihao yang/food.txt').read().split('\n') # 自定义去除词库
exbody = open('/users/emilywang/shihao yang/body.txt').read().split('\n') # 自定义去除词库
exmedi = open('/users/emilywang/shihao yang/medical.txt').read().split('\n') # 自定义去除词库
exnutri = open('/users/emilywang/shihao yang/nutrition.txt').read().split('\n') # 自定义去除词库
eximportant = ['有效','增强','补充','增长','增加','促进','含有','有助于','有利于','好处','支持','产生','作用','抑制','富含','保持','提高','必需','供给']
total = exfood + exbody + exmedi + exnutri
del exfood,exbody,exmedi,exnutri
total.remove('口服')
total.remove('抑制')
# 文本分词
stopwords = open('/users/emilywang/shihao yang/stopword.txt').read().split('\n') # 自定义去除词库
stopwords.append("\n")
#print(remove_words)

def readfile():
    fn = open('/users/emilywang/shihao yang/tnb.txt') # 打开文件
    string_data = fn.read() # 读出整个文件
    fn.close() # 关闭文件
    
    # Removing Square Brackets and Extra Spaces in Texts
    string_data = re.sub(r'\[[0-9]*\]', ' ', string_data)
    string_data = re.sub(r'\s+', ' ', string_data)
    string_data = re.sub('-', '', string_data)
    
    return string_data

def build_semantic_net_zh(text, display=False, display_name='SemanticNet'):
    
    try:
        line = dict()
        sentences = list(sent_tokenize_chinese(text))
        for sent in sentences:
            words = pseg.cut(sent)
            words = [(word, pos) for word, pos in words]
            s, v, o = False, False, False
            
            for i in range(0, len(words)):
                word, pos = words[i]
                if word not in stopwords:
                    if pos[0] == 'n':
                        if s is False:
                            s = word
                        elif s == words[i-1][0]:
                            s += word
                    if pos[0] == 'v':
                        if (s is not False) and (v is False):
                            v = word
                        elif v == words[i-1][0]:
                            v += word
                    if pos[0] == 'n':
                        if (s is not False) and (v is not False) and (o is False):
                            o = word
                        elif o == words[i-1][0]:
                            o += word
            
                #print(word, pos, ';\t\t\t', s, v, o)
            
            if (s is not False) and (v is not False) and (o is not False):
                s, v, o = list(word_tokenize_chinese(s)), list(word_tokenize_chinese(v)), list(word_tokenize_chinese(o))
                for s_word in s:
                    if len(s_word) > 8:
                        s_tem = pseg.cut(s_word, use_paddle=True)
                        s_tem = [(word, pos) for word, pos in s_tem]
                        new_s_word = ''
                        for s_tem_word in s_tem:
                            if s_tem_word[1] == 'n':
                                new_s_word += s_tem_word[0]
                        s_word = new_s_word
                    for v_word in v:
                        if len(v_word) > 8:
                            v_tem = pseg.cut(v_word, use_paddle=True)
                            v_tem = [(word, pos) for word, pos in v_tem]
                            for v_tem_word in v_tem:
                                if v_tem_word[1] == 'v':
                                    v_word = v_tem_word[0]
                        for o_word in o:
                            if len(o_word) > 8:
                                o_tem = pseg.cut(o_word, use_paddle=True)
                                o_tem = [(word, pos) for word, pos in o_tem]
                                for o_tem_word in o_tem:
                                    if o_tem_word[1] == 'n':
                                        o_word = o_tem_word[0]
                            if (s_word, v_word, o_word) not in line.keys():
                                line[(s_word, v_word, o_word)] = 1
                            else:
                                line[(s_word, v_word, o_word)] += 1
                            #semantic_net.add_edge(s_word, o_word, type=v_word)
                            #print("[{}] [{}] [{}]".format(s_word, v_word, o_word))
            #print('------------------------------------')
        '''    
        if display:
            semantic_net.export(display_name, directed=True, weighted=0.3)
            webbrowser.open('file://' + os.path.realpath(display_name+'/index.html'))
    
        return semantic_net
        '''
        return line
    except Exception as e:
        print_error(e)
        return None

def rungraphorg(line,display_name='SemanticNet'):
    semantic_net = Graph()
    line = np.array(pd.Series(line).reset_index())
    for node2node in line:  
            semantic_net.add_edge(node2node[0], node2node[2], type=node2node[1],weight = node2node[3])
    semantic_net.export(display_name, directed=True, weighted=0.3)
    webbrowser.open('file://' + os.path.realpath(display_name+'/index.html'))


def rungraph(line,display_name='SemanticNet'):
    semantic_net = Graph()
    line = np.array(pd.Series(line).reset_index())
    for node2node in line:  
        if node2node[0] in total and node2node[2] in total:
            print(node2node[0], node2node[1],node2node[2])
            semantic_net.add_edge(node2node[0], node2node[2], type=node2node[1],weight = node2node[3])
    semantic_net.export(display_name, directed=True, weighted=0.3)
    webbrowser.open('file://' + os.path.realpath(display_name+'/index.html'))
 
def rungraph2(line,display_name='SemanticNet'):
    semantic_net = Graph()
    line = np.array(pd.Series(line).reset_index())
    for node2node in line:  
        if node2node[0] in total or node2node[2] in total:
            semantic_net.add_edge(node2node[0], node2node[2], type=node2node[1],weight = node2node[3])
    semantic_net.export(display_name, directed=True, weighted=0.3)
    webbrowser.open('file://' + os.path.realpath(display_name+'/index.html'))
 
def rungraph3(line,display_name='SemanticNet'):
    semantic_net = Graph()
    line = pd.Series(line).reset_index()
    line.columns = ['s','v','o','weight']
    s_count = line['s'].value_counts()
    o_count = line['o'].value_counts()
    line = np.array(line)
    for node2node in line:  
        if (node2node[0] in total and node2node[2] in total) or (s_count[node2node[0]] > 1 and o_count[node2node[2]] > 1):
            semantic_net.add_edge(node2node[0], node2node[2], type=node2node[1],weight = node2node[3])
    semantic_net.export(display_name, directed=True, weighted=0.3)
    webbrowser.open('file://' + os.path.realpath(display_name+'/index.html'))
 

string_data = readfile()
line = build_semantic_net_zh(string_data, True)
rungraphorg(line)
rungraph(line)
rungraph2(line)
rungraph3(line)

