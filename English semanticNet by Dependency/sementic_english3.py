#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:45:06 2020

@author: ShihaoYang
"""
import spacy
import os
import jieba
import re
from spacy import displacy

sent = 'Certain conditions may cause you to have more gas or to have more symptoms when you have a normal amount of gas in your digestive tract.'

os.chdir('/Users/emilywang/shihao yang')

nlp = spacy.load("en")
SUBJ = ["nsubj", "nsubjpass"]
VERB = ["ROOT"]
OBJ = ["dobj", "pobj", "dobj"]
modifier = ['amod', 'nounmod', 'nummod', 'quantmod', 'compound', 'relcl', 'neg', 'advmod']

processed_sent = nlp(sent.lower())

nlp = spacy.load('en')
doc = nlp(sent)
displacy.serve(doc, style='dep')

print("increased pressure on the abdomen from being overweight, obese, or pregnant|certain medicines, including|    |those used to treat asthma—a long-lasting disease in the lungs that makes a child or teen extra sensitive to things that he or she is allergic to|antihistamines—medicines that treat allergy symptoms|painkillers|sedatives—medicines that help put someone to sleep|antidepressants—medicines that treat depression|||smoking,which is more likely with teens than younger children, or inhaling secondhand smoke|")