#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:30:01 2020

@author: ShihaoYang
"""

import spacy

nlp = spacy.load('en')

doc = nlp( "In absolute numbers, the United States, Brazil, and the People's Republic of China are the world's three largest consumers of beef" )
for token in doc:
    print('{0}({1}) <-- {2} -- {3}({4})'.format(token.text, token.tag_, token.dep_, token.head.text, token.head.tag_))


def extractmain(doc):
    for word in doc:
        if word.dep_ == 'ROOT':        
            mainword = word.text
    
    specialwords = list(map(lambda x : x.text,list(doc.ents)))
    
    def findword(specialwords,word):
        for item in specialwords:
            if word in item:
                return item
        return 0
    
    keywords = []
    for word in doc:
        anc = list(map(lambda x : x.text,list(word.ancestors)))
        if word.text == mainword:
            keywords.append(word.text)
            continue
        if mainword in anc and word.tag_ in ['NN','NNS','NNP']:
            if len(anc) <= 4:
                k = findword(specialwords,word.text)
                if k == 0:
                    keywords.append(word.text)
                elif k not in keywords:
                    keywords.append(k)
            else:
                flag = 1
                for wo in anc:
                    if wo == mainword:
                        continue
                    if wo not in ' '.join(specialwords):
                        flag = 0
                        break
                k = findword(specialwords,word.text)
                if flag == 1 and k not in keywords:
                    keywords.append(k)
    return keywords

doc = nlp("Barack Obama is an American politician who served as the 44th President of the United States from 2009 to 2017.")
doc = nlp( "On physical examination, hypertension may be associated with the presence of changes in the optic fundus seen by ophthalmoscopy" )
doc = nlp( "Mrs. Robinson graduated from the Wharton School of the University of Pennsylvania in 1980" )
doc = nlp("The big grey dog ate all of the chocalate")
doc = nlp("The most healthful calcium sources are green leafy vegetables and legumes")
doc = nlp("Vitamin D controls your body's use of calcium.")
doc = nlp("Steroid medications, such as prednisone, are a common cause of bone loss and fractures.")

print(extractmain(doc))

spacy.displacy.serve(doc, style='dep')


# 利用空格分开
print(doc.text.split())
# 利用token的.orth_方法，可以识别标点符号
print([token.orth_ for token in doc])
# 带下划线的方法返回字符、不带下划线的方法返回数字
print([(token, token.orth_, token.orth) for token in doc])
# 分词，去除标点和空格
print([token.orth_ for token in doc if not token.is_punct | token.is_space])
# 标准化到基本形式
practice = "practice practiced practicing"
nlp_practice = nlp(practice)
print([word.lemma_ for word in doc])
wiki_obama = """Barack Obama is an American politician who served as the 44th President of the United States from 2009 to 2017. He is the first African American to have served as president, as well as the first born outside the contiguous United States."""
nlp_obama = nlp(wiki_obama)
print([(i, i.label_, i.label) for i in nlp_obama.ents])



