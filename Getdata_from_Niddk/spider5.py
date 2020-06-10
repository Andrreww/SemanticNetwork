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
        self.col = self.db['Liver-Disease']

    def get_html(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read()
        return html
    
    def spider_main(self):        
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
            info = selector.xpath('//div[@class="dk-box-content"]//text()')[1]
            data['basic_info'] = str(info)
            #print(newurl+tr+k[0])
            data['common'],data['who'] = self.find_definition(newurl+tr+k[0])
            data['symptom'],data['cause'],data['help'] = self.find_symptoms(newurl+tr+k[1])
            data['diet'],data['caneat'],data['noteat'] = self.find_diet(newurl+tr+k[4])
            print(item)
            self.col.insert_one(data)
        return
    
    def findde(self,h2):
        common = ''
        who = ''
        try:
            if 'common' in h2.text or 'Common' in h2.text :
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        common = ''
                    if h2.text != None:
                        common += re.sub(r'\n','|',h2.text.strip())
                        common += '|'
                        if h2.name == 'ul':
                            return common,who
            if 'who' in h2.text or 'Who' in h2.text:
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        who= ''
                    if h2.text != None:
                        who += re.sub(r'\n','|',h2.text.strip())
                        who += '|'
                        if h2.name == 'ul':
                            return common,who
        except:
            pass
        return common,who
    def find_definition(self,url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        ret = soup.find("div",class_="health-detail-content")
        h2find = ret.find_all("h2")
        
        common = ''
        who = ''
        for h2 in h2find:
            s,c = self.findde(h2)
            if common == '':
                common += s
            if who == '':    
                who += c
        return common,who
    
    def findh2(self,h2):
        symptom = ''
        cause = ''
        needhelp = ''
        try:
            if 'symptom' in h2.text or 'Symptom' in h2.text :
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        symptom = ''
                    if h2.text != None:
                        symptom += re.sub(r'\n','|',h2.text.strip())
                        symptom += '|'
                        if h2.name == 'ul':
                            return symptom,cause,needhelp
            if 'cause' in h2.text or 'causing' in h2.text:
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        cause= ''
                    if h2.text != None:
                        cause += re.sub(r'\n','|',h2.text.strip())
                        cause += '|'
                        if h2.name == 'ul':
                            return symptom,cause,needhelp
            if 'help' in h2.text or 'care' in h2.text:
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        needhelp = ''
                    if h2.text != None:
                        needhelp += re.sub(r'\n','|',h2.text.strip())
                        needhelp += '|'
                        if h2.name == 'ul':
                            return symptom,cause,needhelp
        except:
            pass
        return symptom,cause,needhelp
    def find_symptoms(self,url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        ret = soup.find("div",class_="health-detail-content")
        h2find = ret.find_all("h2")
        
        symptom = ''
        cause = ''
        needhelp = ''
        for h2 in h2find:
            s,c,h = self.findh2(h2)
            if symptom == '':
                symptom += s
            if cause == '':    
                cause += c
            if needhelp == '':
                needhelp += h
        return symptom,cause,needhelp
                
    def finddiet(self,h2):
        diet = ''
        caneat = ''
        noteat = ''
        try:
            if 'diet' in h2.text:
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        diet = ''
                    if h2.text != None:
                        diet += re.sub(r'\n','|',h2.text.strip())
                        diet += '|'
                        if h2.name == 'ul':
                            return diet,caneat,noteat
                return diet,caneat,noteat
            if 'eat' in h2.text and 'avoid' not in h2.text:
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        caneat = ''
                    if h2.text != None:
                        caneat += re.sub(r'\n','|',h2.text.strip())
                        caneat += '|'
                        if h2.name == 'ul':
                            return diet,caneat,noteat
            if 'eat' in h2.text and ('avoid' in h2.text or 'limit' in h2.text):
                while(h2.next_sibling.name != 'h2'):
                    h2 = h2.next_sibling
                    if h2.name == None:
                        continue
                    if h2.name == 'ul':
                        noteat = ''
                    if h2.text != None:
                        noteat += re.sub(r'\n','|',h2.text.strip())
                        noteat += '|' 
                        if h2.name == 'ul':
                            return diet,caneat,noteat
        except:
            pass
        return diet,caneat,noteat
    
    def find_diet(self,url):
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        ret = soup.find("div",class_="health-detail-content")
        h2find = ret.find_all("h2")
        
        diet,caneat,noteat = '','',''
        for h2 in h2find:
            s,c,h = self.finddiet(h2)
            if diet == '':
                diet += s
            if caneat == '':    
                caneat += c
            if noteat == '':
                noteat += h
        return diet,caneat,noteat
                
handler = CrimeSpider()
handler.spider_main()
