#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 12:59:50 2020

@author: ShihaoYang
"""
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re
import sys
import os
import bs4 as bs
import urllib.request
import re
import nltk
from nltk import word_tokenize, pos_tag
from nltk.tokenize.treebank import TreebankWordDetokenizer
import spacy
import textacy
import pattern3
from pattern3.graph import Graph
import webbrowser
import pandas
import pickle
from colorama import Fore, Style


conn = pymongo.MongoClient(host='localhost', port=27017)
db = conn.testdb
col = db['digestive-diseases']
key_words = ['lifestyle changes','feeding changes','medicines','surgery','antibiotics','endoscopy','gluten-free','colonoscopy','sigmoidoscopy','biofeedback','rest','liquid diet','quit smoking','blood glucose levels','mental health','bladder training','physical therapy','bathroom habits','phlebotomy','Weight']
for x in col.find():
    print(x['treatment'])
    print('\n')

col = db['digestive-diseases']
key_words=['children',]
for x in col.find():
    print(x['common'])
    print('\n')

key_words=['teens','twenties',]
for x in col.find():
    print(x['who'])
    print('\n')

key_words=['teens','twenties',]
for x in col.find():
    print(x['symptom'])
    print('\n')

w = 'bags and rooms'
def lemmatize(words):

    lemmatizer = nltk.stem.WordNetLemmatizer()
    lemmatized_word = []
    for word, tag in pos_tag(word_tokenize(words)):
        if word in ['replace','instead']:
            break
        wntag = tag[0].lower()
        wntag = wntag if wntag == 'n' else None
        if wntag:
            word = lemmatizer.lemmatize(word)
            lemmatized_word.append(word)
    return lemmatized_word

def findcaneat():
    wdict = {}
    #nlp = spacy.load('en')
    for x in col.find():
        temp = re.sub('\|',' ',x['caneat'])
        sentences = nltk.sent_tokenize(temp)
        w = []
        for i in sentences:
            w.extend(lemmatize(i))
        wdict[x['name']] = list(set(w))
    return wdict
def findnoteat():
    wnotdict = {}
    #nlp = spacy.load('en')
    for x in col.find():
        temp = re.sub('\|',' ',x['noteat'])
        sentences = nltk.sent_tokenize(temp)
        w = []
        for i in sentences:
            w.extend(lemmatize(i))
        wnotdict[x['name']] = list(set(w))
    return wnotdict
wnotdict = findnoteat()