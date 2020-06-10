#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 11:20:36 2020

@author: ShihaoYang
"""

import urllib
import importlib,sys
importlib.reload(sys)
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import os
os.chdir('/Users/emilywang/shihao yang')


def parse(DataIO, save_path):
 
    #用文件对象创建一个PDF文档分析器
    parser = PDFParser(DataIO)
    #创建一个PDF文档
    doc = PDFDocument()
    #分析器和文档相互连接
    parser.set_document(doc)
    doc.set_parser(parser)
    #提供初始化密码，没有默认为空
    doc.initialize()
    #检查文档是否可以转成TXT，如果不可以就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        #创建PDF资源管理器，来管理共享资源
        rsrcmagr = PDFResourceManager()
        #创建一个PDF设备对象
        laparams = LAParams()
        #将资源管理器和设备对象聚合
        device = PDFPageAggregator(rsrcmagr, laparams=laparams)
        #创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmagr, device)
 
        #循环遍历列表，每次处理一个page内容
        #doc.get_pages()获取page列表
        for page in doc.get_pages():
            interpreter.process_page(page)
            #接收该页面的LTPage对象
            layout = device.get_result()
            #这里的layout是一个LTPage对象 里面存放着page解析出来的各种对象
            #一般包括LTTextBox，LTFigure，LTImage，LTTextBoxHorizontal等等一些对像
            #想要获取文本就得获取对象的text属性
            for x in layout:
                try:
                    if(isinstance(x, LTTextBoxHorizontal)):
                        with open('%s' % (save_path), 'a') as f:
                            result = x.get_text()
                            print (result)
                            f.write(result + "\n")
                except:
                    print("Failed")
 
 
if __name__ == '__main__':
    #解析本地PDF文本，保存到本地TXT
    with open(r'book.pdf','rb') as pdf_html:
        parse(pdf_html, r'book.txt')
 
    #解析网络上的PDF，保存文本到本地
    # url = "https:"
    # pdf_html = urllib.urlopen(url).read()
    # DataIO = StringIO(pdf_html)
    # parse_pdf(DataIO, r'E:\parse_pdf')

in_file = open(r'book.txt','r')
text_line = in_file.readline()
count = 0
while text_line:
    sentence = text_line.strip()
    if sentence == 'Etiology (Cause/Contributing Risk Factors)':
        count+= 1
    text_line = in_file.readline()



import tabula
import numpy as np
import pandas as pd
df = tabula.read_pdf('book.pdf',encoding='utf-8', pages='all')
df = df[9:]
temp = df[67]
temp.iloc[4,1] = temp.iloc[4,1] + temp.iloc[5,1] +temp.iloc[6,1] +temp.iloc[7,1] +temp.iloc[8,1] +temp.iloc[9,1]
k = temp.iloc[0,1] + temp.iloc[1,1] +temp.iloc[2,1] +temp.iloc[3,1]
temp.columns = [temp.columns[0],temp.columns[1]+k]
temp.dropna(inplace = True)
df[67] = temp
col = []
for item in df:
    col.append(list(item.columns))
l = [1] * len(df)
for i in range(1,len(df)):
    if df[i].columns[0] != col[0][0]:
        temp = df[i]
        dic = dict(zip(temp.columns,temp.columns))
        temp = temp.append(dic,ignore_index=True)
        temp.columns = df[i-1].columns
        df[i-1] = pd.concat([df[i-1],temp])
        l[i] = 0
newdf = []
for i in range(len(df)):
    if l[i] == 1:
        newdf.append(df[i])
newdf[45] = newdf[45].head(5)

df = tabula.read_pdf('book.pdf',encoding='utf-8', pages='all',pandas_options={'header': None})
mul = df[:9]
for i in mul:
    i.dropna(inplace = True)
prolist = []
for i in mul:
    prolist += list(i.iloc[:,0])
prolist = prolist[1:]

in_file = open(r'book.txt','r')
text_line = in_file.readline()
text = []
flag = 0
while text_line:
    sentence = text_line.strip()
    if sentence != '':
        if sentence == 'Definition':
            flag = 1
        if flag == 1:
            text.append(sentence)
        if sentence == 'Signs/Symptoms (Defining Characteristics)':
            flag =0
    text_line = in_file.readline()



import pymongo
import re
conn = pymongo.MongoClient(host='localhost', port=27017)
db = conn.testdb
col = db['bookspider']


i = 0
flag = 0
for j in range(len(text)):
    sentence = text[j]
    if sentence == 'Definition':
        dic = {}
        dic['name'] = prolist[i]
        flag = 1
        continue
    if sentence == 'Etiology (Cause/Contributing Risk Factors)':
        flag = 2
        continue
    if sentence == 'Signs/Symptoms (Defining Characteristics)':
        flag = 0
        newdf[i].columns = newdf[0].columns
        dic.update(dict(zip(newdf[i]['Nutrition Assessment Category'],newdf[i]['Potential Indicators of this Nutrition Diagnosis (one or more must be present)'])))
        col.insert(dic)
        dic ={}
        print(i)
        i+=1
    if flag == 1:
        if 'Definition' in dic:
            dic['Definition'] += '|'
            dic['Definition']  += text[j]
        else:
            dic['Definition']  = text[j]
    elif flag == 2:
        if 'Etiology' in dic:
            dic['Etiology'] += '|'
            dic['Etiology']  += text[j]
        else:
            dic['Etiology']  = text[j]
    
for x in col.find():
    if 'problems:' in x['Etiology']:
        
        
    
    
    
    