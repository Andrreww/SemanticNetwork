#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 16:44:11 2020

@author: ShihaoYang
"""

import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

conn = pymongo.MongoClient(host='localhost', port=27017)
db = conn.testdb
col = db['food_nutrition']

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read().decode('gbk')
    return html


url = 'http://jib.xywy.com/il_sii/gaishu/1.htm'
html = get_html(url)

selector = etree.HTML(html)
title = selector.xpath('//title/text()')[0]
category = selector.xpath('//div[@class="wrap mt10 nav-bar"]/a/text()')
desc = selector.xpath('//div[@class="jib-articl-con jib-lh-articl"]/p/text()')
ps = selector.xpath('//div[@class="mt20 articl-know"]/p')

infobox = []
for p in ps:
    info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
    infobox.append(info)

basic_data = {}
basic_data['category'] = category
basic_data['name'] = title.split('的简介')[0]
basic_data['desc'] = desc
basic_data['attributes'] = infobox
return basic_data

ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')
infobox = []
for p in ps:
    info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
    infobox.append(info)
return infobox

drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]

