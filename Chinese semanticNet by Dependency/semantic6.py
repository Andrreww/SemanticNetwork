#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 13:34:19 2020

@author: ShihaoYang
"""

from pyltp  import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
from pyltp import NamedEntityRecognizer
import os
import jieba
import re
os.getcwd()
os.chdir('/Users/emilywang/shihao yang')
os.getcwd()

LTP_DATA_DIR='/Users/emilywang/shihao yang/ltp_data_v3.4.0/'

cws_model_path=os.path.join(LTP_DATA_DIR,'cws.model')
segmentor=Segmentor()
segmentor.load(cws_model_path)

pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger() # 初始化实例
postagger.load(pos_model_path)  # 加载模型

par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
parser = Parser() # 初始化实例
parser.load(par_model_path)  # 加载模型

class Sentence(object):

    def __init__(self,text):
        self.text = text
        self.data = dict()
        
    def SentS(self):
        sents = SentenceSplitter.split(self.text)  # 分句
        return sents
    
    def getLTPAnalysis(self, sentence):

        words=segmentor.segment(sentence)
        #print('\t'.join(words))

        postags = postagger.postag(words)  # 词性标注
        #print('\t'.join(postags))
        arcs = parser.parse(words, postags)  # 句法分析
        rely_id = [arc.head for arc in arcs]              # 提取依存父节点id
        relation = [arc.relation for arc in arcs]         # 提取依存关系
        #heads = ['Root' if id == 0 else words[id-1] for id in rely_id]  # 匹配依存父节点词语
        #for i in range(len(words)):
            #print(relation[i] + '(' + words[i] + ', ' + heads[i] + ')')
            
        return words,postags,rely_id,relation

    def getWord(self, words,postags,rely_id,relation,_id,wType):
        sbv = None
        for i in range(len(words)):
            if relation[i] == wType and rely_id[i] == (_id)+1:
                return i
        return sbv
    
    def getpron(self,words,postags,rely_id,relation,_id):
        flag = None
        for i in range(len(words)):
            if relation[i] == 'ADV' and postags[i] == 'p' and rely_id[i] == (_id)+1:
                flag = i
                break
        if flag == None:
            return None
        pob = None
        vob_of_pob = None
        pob = self.getWord(words,postags,rely_id,relation,flag,'POB')
        if pob:
            vob_of_pob = self.getWord(words,postags,rely_id,relation,pob,'VOB')
            if vob_of_pob:
                return vob_of_pob
            else:
                return pob
        return None
        
    def getatt_of_sbv(self,words,postags,rely_id,relation,_id):
        for i in range(len(words)):
            if relation[i] == 'ATT' and rely_id[i] == (_id)+1 and (postags[i]=='a' or postags[i]=='n'):
                return i
        return None
    def getFirstNotNone(self, array):
        for word in array:
            if word is not None:
                return word
        return None
    
    def getMainsent(self,realsbv,sentence):
        re = ''
        words,postags,rely_id,relation = self.getLTPAnalysis(sentence)
        #hed = self.getHED(array)
        if 0 not in rely_id:
            return None,None
        
        hed = rely_id.index(0)
        sbv = self.getWord(words,postags,rely_id,relation,hed, 'SBV')  # 主语
        vob = self.getWord(words,postags,rely_id,relation,hed, 'VOB')  # 宾语
        fob = self.getWord(words,postags,rely_id,relation,hed, 'FOB')  # 后置宾语
        ###############
        if sbv == None:
            reals =  realsbv
        elif postags[sbv] == 'r' and realsbv != None:
            reals =  realsbv
        else:
            reals = words[sbv]
        
        if reals == None:
            return None,None
        if sbv != None and postags[sbv] == 'n':
            temp = self.getatt_of_sbv(words,postags,rely_id,relation,sbv)
            if temp != None:
                if words[sbv] not in self.data.keys():
                    self.data[words[sbv]] = [words[temp]]
                else:
                    self.data[words[sbv]].append(words[temp])
        if sbv != None:
            sbvcoo = self.getWord(words,postags,rely_id,relation,sbv, 'COO')
            if sbvcoo != None:
                reals += words[sbvcoo]
        ###############
        if postags[hed] == 'a':
            temp = self.getpron(words,postags,rely_id,relation,hed)
            if temp!= None:
                re = '{} {} {}'.format(reals, words[hed], words[temp])
            elif sbv != None:
                temp = self.getatt_of_sbv(words,postags,rely_id,relation,sbv)
                if temp != None:
                    re = '{} {} {}'.format(words[temp] + reals, words[hed], '')
                else:
                    re = '{} {} {}'.format(reals, words[hed], '')
            return reals,re
        
        finalvob = self.getFirstNotNone([vob, fob])
        if finalvob != None:
            temp = self.getWord(words,postags,rely_id,relation,finalvob, 'VOB')
            if temp != None:
                re = '{} {} {}'.format(reals, words[hed], words[finalvob] + words[temp])
            else:
                re = '{} {} {}'.format(reals, words[hed], words[finalvob])
        else:
            re = '{} {} {}'.format(reals, words[hed], '')
        return reals,re
    def getMain(self,sentence):
        sentence = re.sub(' ','。',sentence)
        sentence = re.sub('，','。',sentence)
        sents = SentenceSplitter.split(sentence)
        reals = None
        for s in sents:
            reals,res = self.getMainsent(reals,s)
            if res != None:
                print(res)
    def gettextmain(self):
        sents = self.SentS()
        for s in sents:
            self.getMain(s)
            
s = Sentence('陈欣婕今天真好看。她今天中午吃炸鸡')
s.gettextmain()

def readfile():
    fn = open('/users/emilywang/shihao yang/beef.txt') # 打开文件
    string_data = fn.read() # 读出整个文件
    fn.close() # 关闭文件
    
    # Removing Square Brackets and Extra Spaces in Texts
    string_data = re.sub(r'\[[0-9]*\]', ' ', string_data)
    string_data = re.sub(r'\s+', ' ', string_data)
    string_data = re.sub('-', '', string_data)

    return string_data
string = readfile()
s = Sentence(readfile())
s.gettextmain()
s.data

string = readfile()
s = Sentence('苹果和香蕉都是水果')
s.gettextmain()
s.data