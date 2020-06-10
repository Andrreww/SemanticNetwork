#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 09:48:42 2020

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

sents = SentenceSplitter.split('元芳你怎么看？我就趴窗口上看呗！糖尿病有传染性，它不适合运动')  # 分句

print('\n'.join(sents))

#################seg
LTP_DATA_DIR='/Users/emilywang/shihao yang/ltp_data_v3.4.0/'
cws_model_path=os.path.join(LTP_DATA_DIR,'cws.model')
segmentor=Segmentor()
segmentor.load(cws_model_path)
words=segmentor.segment('熊高雄你吃饭了吗')
print(type(words))
print('\t'.join(words))
segmentor.release()

segmentor = Segmentor()  # 初始化实例
segmentor.load_with_lexicon(cws_model_path) # 加载模型，第二个参数是您的外部词典文件路径
segmentor.load(cws_model_path)
words = segmentor.segment('亚硝酸盐是一种化学物质')
print('\t'.join(words))
segmentor.release()

#################pos
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger() # 初始化实例
postagger.load(pos_model_path)  # 加载模型
words = ['元芳', '你', '怎么', '看']  # 分词结果
postags = postagger.postag(words)  # 词性标注
print('\t'.join(postags))
postagger.release()  # 释放模型

#################parser
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
parser = Parser() # 初始化实例
parser.load(par_model_path)  # 加载模型
words = ['元芳', '你', '怎么', '看']
postags = ['nh', 'r', 'r', 'v']
arcs = parser.parse(words, postags)  # 句法分析

rely_id = [arc.head for arc in arcs]              # 提取依存父节点id
relation = [arc.relation for arc in arcs]         # 提取依存关系
heads = ['Root' if id == 0 else words[id-1] for id in rely_id]  # 匹配依存父节点词语
for i in range(len(words)):
    print(relation[i] + '(' + words[i] + ', ' + heads[i] + ')')



parser.release()   

        
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
            
        return words,rely_id,relation

    def getWord(self, words,rely_id,relation,hed,wType):
        sbv = None
        for i in range(len(words)):
            if relation[i] == wType and rely_id[i] == hed+1:
                sbv = words[i]
        return sbv

    def getFirstNotNone(self, array):
        for word in array:
            if word is not None:
                return word
        return None

    def getMain(self,sentence):
        re = ''
        words,rely_id,relation = self.getLTPAnalysis(sentence)
        #hed = self.getHED(array)
        if 0 in rely_id:
            hed = rely_id.index(0)
            sbv = self.getWord(words,rely_id,relation,hed, 'SBV')  # 主语
            vob = self.getWord(words,rely_id,relation,hed, 'VOB')  # 宾语
            fob = self.getWord(words,rely_id,relation,hed, 'FOB')  # 后置宾语

            adv = self.getWord(words,rely_id,relation,hed, 'ADV')  # 定中
            pob = self.getWord(words,rely_id,relation,hed, 'POB')  # 介宾如果没有主语可做主语

            zhuWord = self.getFirstNotNone([sbv, pob])  # 最终主语
            weiWord = words[hed] # 最终谓语
            binWord = self.getFirstNotNone([vob, fob, pob])  # 最终宾语

            re = '{} {} {}'.format(zhuWord, weiWord, binWord)

        return re.replace('None', ' ')
    
    def gettextmain(self):
        sents = self.SentS()
        for s in sents:
            print(self.getMain(s))
            
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