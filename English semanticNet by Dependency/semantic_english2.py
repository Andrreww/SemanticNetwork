#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 09:53:45 2020

@author: emilywang
"""

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

def include(list_1, list_2):
    for element in list_1:
        if element in list_2:
            return True
    return False


def no_digit_in_list(input_list):
    for string in input_list:
        if string.isdigit():
            return False
    return True


def print_error(error):
    print(Fore.RED)
    print('Exception Found:', error)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, f_name, exc_tb.tb_lineno)
    print(Style.RESET_ALL)

def lemmatize(words):
    lemmatizer = nltk.stem.WordNetLemmatizer()
    lemmatized_word = []
    for word, tag in pos_tag(word_tokenize(words)):
        wntag = tag[0].lower()
        wntag = wntag if wntag in ['a', 'r', 'n', 'v'] else None
        if wntag:
            word = lemmatizer.lemmatize(word)
            lemmatized_word.append(word)

    return TreebankWordDetokenizer().detokenize(lemmatized_word)

def match_svo(s_tuple, v_tuple, o_tuple):

    best_svo = []
    for (s, s_index) in s_tuple:

        best_v, best_v_dist = '', 100
        for (v, v_index) in v_tuple:
            v_dist = abs(s_index - v_index)
            if v_dist < best_v_dist:
                best_v = v
                best_v_dist = v_dist
                best_v_index = v_index

        best_o, best_o_dist = '', 100
        for (o, o_index) in o_tuple:
            o_dist = abs(best_v_index - o_index)
            if o_dist < best_o_dist:
                best_o = o
                best_o_dist = o_dist

        best_svo.append((s, best_v, best_o))

    return best_svo
# ***** Main Functions for Creating Semantic Network in English ***** #

semantic_net = Graph()

nlp = spacy.load("en_core_web_sm")
SUBJ = ["nsubj", "nsubjpass"]
VERB = ["ROOT"]
OBJ = ["dobj", "pobj", "dobj"]
modifier = ['amod', 'nounmod', 'nummod', 'quantmod', 'compound', 'relcl', 'neg', 'advmod']

stopwords = open('/users/emilywang/shihao yang/stopword.txt').read().split('\n') # 自定义去除词库
stopwords.append("\n")

text = open('/users/emilywang/shihao yang/beef_english.txt').read()
sentences = nltk.sent_tokenize(text)
#title = 'beef'
print("Start Building the Semantic Network... Title: {}".format(title))

# analyze the text sentence by sentence
line = dict()
for sent in sentences:
    #sent = sentences[0]
    processed_sent = nlp(sent.lower())
    subject_, verb_, object_ = [], [], []
    # analyze the sentence word by word (tok by tok)
    for i in range(0, len(processed_sent)):
        tok = processed_sent[i]

        # process the subjects
        if tok.dep_ in SUBJ:
            if len(list(tok.children)) > 0:
                subject_wordlist = []
                for child in tok.children:
                    if child.dep_ in modifier:
                        subject_wordlist.append(child.text)
                subject_wordlist.append(tok.lemma_)
                subject_word = ' '.join(subject_wordlist)
                subject_.append((subject_word, i))
            if len(subject_) == 0:
                subject_.append((tok.lemma_, i))

        # process the verbs
        elif tok.dep_ in VERB or tok.pos_ == 'VERB':
            verb_.append((tok.lemma_, i))

        # process the objects
        elif tok.dep_ in OBJ:
            if len(list(tok.children)) > 0:
                object_wordlist = []
                for child in tok.children:
                    if child.dep_ in modifier:
                        object_wordlist.append(child.text)
                object_wordlist.append(tok.lemma_)
                object_word = ' '.join(object_wordlist)
                object_.append((object_word, i))
            if len(object_) == 0:
                object_.append((tok.lemma_, i))

    # record the result if S,V,O are all found in this sentence
    if (len(subject_) > 0) and (len(verb_) > 0) and (len(object_) > 0):
        best_svo = match_svo(subject_, verb_, object_)
        for (s, v, o) in best_svo:
            if no_digit_in_list([s, v, o]):
                if (s, v, o) not in line.keys():
                    line[(s, v, o)] = 1
                else:
                    line[(s, v, o)] += 1

    # use textacy to find S,V,O
    textacy_result = list(textacy.extract.subject_verb_object_triples(processed_sent))

    # extract the result of textacy
    for result in textacy_result:
        s, v, o = result[0].text, result[1].text, result[2].text
        s, v, o = lemmatize(s), lemmatize(v), lemmatize(o)
        if no_digit_in_list([s, v, o]):
            if (s, v, o) not in line.keys():
                line[(s, v, o)] = 1
            else:
                line[(s, v, o)] += 1


import numpy as np
import pandas as pd
def rungraphorg(line,display_name='SemanticNet'):
    semantic_net = Graph()
    line = np.array(pd.Series(line).reset_index())
    for node2node in line:  
            semantic_net.add_edge(node2node[0], node2node[2], type=node2node[1],weight = node2node[3])

    semantic_net.export(display_name, directed=True, width=1920, height=1080)
    webbrowser.open('file://' + os.path.realpath(display_name + '/index.html'))
    
rungraphorg(line,'eng_v')