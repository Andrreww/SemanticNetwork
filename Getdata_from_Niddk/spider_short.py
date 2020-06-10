#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 14:34:52 2020

@author: emilywang
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 09:49:29 2020

@author: ShihaoYang
"""
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re
class CrimeSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.conn['testdb']
        self.col = self.db['description_all']

    def get_html(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read()
        return html
    
    def spider_main1(self):        
        url = 'https://www.niddk.nih.gov/health-information/digestive-diseases/abdominal-adhesions'
        html = self.get_html(url)
        selector = etree.HTML(html)
        info = selector.xpath('//nav[@class="dk-leftnav"]//@href')
        k = ['definition-facts','symptoms-causes','diagnosis','treatment','eating-diet-nutrition','clinical-trials']
        t = []
        for p in info:
            t.append(p.split('/')[-1])
        realt = []
        for i in range(len(t)-len(k)):
            if t[i+1:i+len(k)+1] == k:
                realt.append(t[i])
        url = 'https://www.niddk.nih.gov/health-information/digestive-diseases'
        tr = '/'
        for item in realt:
            data = {}
            data['name'] = item
            newurl = url+tr+item
            html = self.get_html(newurl)
            selector = etree.HTML(html)
            info = selector.xpath('//div[@class="dk-box-content"]//text()')
            info = list(map(lambda x: x.strip(),info))
            info2 = [i for i in info if i != '']
            data['definition'] = str(info2[0])
            data['symptoms-causes'] = str(info2[1])
            data['diagnosis'] = str(info2[2])
            data['treatment'] = str(info2[3])
            data['diet'] = str(info2[4])
            print(item)
            self.col.insert_one(data)
        return
    def spider_main2(self):        
        url = 'https://www.niddk.nih.gov/health-information/urologic-diseases/bladder-control-medicines'
        html = self.get_html(url)
        selector = etree.HTML(html)
        info = selector.xpath('//nav[@class="dk-leftnav"]//@href')
        k = ['definition-facts','symptoms-causes','diagnosis','treatment','eating-diet-nutrition','clinical-trials']
        t = []
        for p in info:
            t.append(p.split('/')[-1])
        realt = []
        for i in range(len(t)-len(k)):
            if t[i+1:i+len(k)+1] == k:
                realt.append(t[i])
        url = 'https://www.niddk.nih.gov/health-information/urologic-diseases'
        tr = '/'
        for item in realt:
            data = {}
            data['name'] = item
            newurl = url+tr+item
            html = self.get_html(newurl)
            selector = etree.HTML(html)
            info = selector.xpath('//div[@class="dk-box-content"]//text()')
            info = list(map(lambda x: x.strip(),info))
            info2 = [i for i in info if i != '']
            data['definition'] = str(info2[0])
            data['symptoms-causes'] = str(info2[1])
            data['diagnosis'] = str(info2[2])
            data['treatment'] = str(info2[3])
            data['diet'] = str(info2[4])
            print(item)
            self.col.insert_one(data)
        return
    def spider_main3(self):        
        url = 'https://www.niddk.nih.gov/health-information/liver-disease/alagille-syndrome'
        html = self.get_html(url)
        selector = etree.HTML(html)
        info = selector.xpath('//nav[@class="dk-leftnav"]//@href')
        k = ['definition-facts','symptoms-causes','diagnosis','treatment','eating-diet-nutrition','clinical-trials']
        t = []
        for p in info:
            t.append(p.split('/')[-1])
        realt = []
        for i in range(len(t)-len(k)):
            if t[i+1:i+len(k)+1] == k:
                realt.append(t[i])
        realt[0] = 'alagille-syndrome'
        url = 'https://www.niddk.nih.gov/health-information/liver-disease'
        tr = '/'
        for item in realt:
            data = {}
            data['name'] = item
            newurl = url+tr+item
            html = self.get_html(newurl)
            selector = etree.HTML(html)
            info = selector.xpath('//div[@class="dk-box-content"]//text()')
            info = list(map(lambda x: x.strip(),info))
            info2 = [i for i in info if i != '']
            data['definition'] = str(info2[0])
            data['symptoms-causes'] = str(info2[1])
            data['diagnosis'] = str(info2[2])
            data['treatment'] = str(info2[3])
            data['diet'] = str(info2[4])
            print(item)
            self.col.insert_one(data)
        return
    def spider_main(self):
        self.spider_main1()
        self.spider_main2()
        self.spider_main3()
handler = CrimeSpider()
handler.spider_main()
