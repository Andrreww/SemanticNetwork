#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:12:43 2020

@author: ShihaoYang
"""

from py2neo import Graph,Node,Relationship
g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7687,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="wdygcs")

a = Node("Person", name="Alice")
b = Node("Person", name="Bob")
ab = Relationship(a, "KNOWS", b)
g.create(ab)


import pymongo
conn = pymongo.MongoClient(host='localhost', port=27017)
db = conn.testdb
col = db['testcollection']
student1 = {
 'id': '20170202',
 'name': 'Jordan',
 'age': 20,
 'gender': 'male'
}

result = col.insert(student1)
print(result)


import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

class CrimeSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.conn['testdb']
        self.col = self.db['testcollection']

    def get_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('gbk')
        return html

    def url_parser(self, content):
        selector = etree.HTML(content)
        urls = ['http://www.anliguan.com' + i for i in  selector.xpath('//h2[@class="item-title"]/a/@href')]
        return urls

    def spider_main(self):
        for page in range(2758, 11000):
            try:
                basic_url = 'http://jib.xywy.com/il_sii/gaishu/%s.htm'%page
                cause_url = 'http://jib.xywy.com/il_sii/cause/%s.htm'%page
                prevent_url = 'http://jib.xywy.com/il_sii/prevent/%s.htm'%page
                symptom_url = 'http://jib.xywy.com/il_sii/symptom/%s.htm'%page
                inspect_url = 'http://jib.xywy.com/il_sii/inspect/%s.htm'%page
                treat_url = 'http://jib.xywy.com/il_sii/treat/%s.htm'%page
                food_url = 'http://jib.xywy.com/il_sii/food/%s.htm'%page
                drug_url = 'http://jib.xywy.com/il_sii/drug/%s.htm'%page
                data = {}
                data['url'] = basic_url
                data['basic_info'] = self.basicinfo_spider(basic_url)
                data['cause_info'] =  self.common_spider(cause_url)
                data['prevent_info'] =  self.common_spider(prevent_url)
                data['symptom_info'] = self.symptom_spider(symptom_url)
                data['inspect_info'] = self.inspect_spider(inspect_url)
                data['treat_info'] = self.treat_spider(treat_url)
                data['food_info'] = self.food_spider(food_url)
                data['drug_info'] = self.drug_spider(drug_url)
                print(page, basic_url)
                self.col.insert(data)

            except Exception as e:
                print(e, page)
        return

    def basicinfo_spider(self, url):
        html = self.get_html(url)
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

    def treat_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infobox.append(info)
        return infobox

    def drug_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]
        return drugs

    def food_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        divs = selector.xpath('//div[@class="diet-img clearfix mt20"]')
        try:
            food_data = {}
            food_data['good'] = divs[0].xpath('./div/p/text()')
            food_data['bad'] = divs[1].xpath('./div/p/text()')
            food_data['recommand'] = divs[2].xpath('./div/p/text()')
        except:
            return {}

        return food_data

    def symptom_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        symptoms = selector.xpath('//a[@class="gre" ]/text()')
        ps = selector.xpath('//p')
        detail = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            detail.append(info)
        symptoms_data = {}
        symptoms_data['symptoms'] = symptoms
        symptoms_data['symptoms_detail'] = detail
        return symptoms, detail

    '''检查信息解析'''
    def inspect_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        inspects  = selector.xpath('//li[@class="check-item"]/a/@href')
        return inspects

    def common_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//p')
        infobox = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ','').replace('\t', '')
            if info:
                infobox.append(info)
        return '\n'.join(infobox)

    def inspect_crawl(self):
        for page in range(1, 3685):
            try:
                url = 'http://jck.xywy.com/jc_%s.html'%page
                html = self.get_html(url)
                data = {}
                data['url']= url
                data['html'] = html
                self.db['jc'].insert(data)
                print(url)
            except Exception as e:
                print(e)


handler = CrimeSpider()
handler.spider_main()


import json
col_all = db['medical_all']
with open("/Users/emilywang/shihao yang/pycharmproject/QASystemOnHepatopathyKG-master/data/medical.json", encoding="utf-8") as jf:
    str = jf.read()
    data = []
    data.extend(json.loads(str))
    col_all.insert_many(data)

file = open("/Users/emilywang/shihao yang/pycharmproject/QASystemOnHepatopathyKG-master/data/medical.json", 'r', encoding='utf-8')
papers = []
for line in file.readlines():
    dic = json.loads(line)
    col_all.insert_one(dic)
    
    
##############该6129了