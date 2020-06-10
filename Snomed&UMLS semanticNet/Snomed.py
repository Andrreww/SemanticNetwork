from urllib.request import urlopen
from urllib.parse import quote
import pandas as pd
import numpy as np

import json
import pymongo
import re
conn = pymongo.MongoClient(host='localhost', port=27017)
db = conn.testdb
col = db['UMLSnetwork_core']

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN'
version = '2020-03-09'

concept = pd.read_table('/Users/emilywang/shihao yang/snomed/SNOMEDCT_CORE_SUBSET_202002.txt',sep='|')
concept['SNOMED_CID'] = concept['SNOMED_CID'].apply(str)
concept = concept[['SNOMED_CID', 'SNOMED_FSN']].values.tolist()

def typefind(s):
    p1 = re.compile(r'[(](.*?)[)]', re.S)
    return re.findall(p1, s)[-1]
def extractdescription(datalist):
    tempdic = {}
    for i in range(len(datalist)):
        if datalist[i]['type']:
            if datalist[i]['type'] in tempdic:
                if datalist[i]['term'] not in tempdic[datalist[i]['type']]:
                    tempdic[datalist[i]['type']].append(datalist[i]['term'])
            else:
                tempdic[datalist[i]['type']] = [datalist[i]['term']]
    for key in tempdic.keys():
        tempdic[key] = '|'.join(tempdic[key])
    return tempdic

def extractrelation(datalist):
    tempdic = {}
    for i in range(len(datalist)):
        ty = datalist[i]['type']['fsn']['term']
        target = datalist[i]['target']['fsn']['term']
        if ty:
            if ty in tempdic:
                if target not in tempdic[ty]:
                    tempdic[ty].append(target)
            else:
                tempdic[ty] = [target]
    for key in tempdic.keys():
        tempdic[key] = '|'.join(tempdic[key])
    return tempdic

for i in range(len(concept)):
    try:
        dic = {}
        url = baseUrl + '/browser/' + edition + '/' + version + '/concepts/' + concept[i][0]
        response = urlopen(url).read()
        data = json.loads(response.decode('utf-8'))
        dic['name'] = data['pt']['term']
        dic['type'] = typefind(data['fsn']['term'])
        dic.update(extractdescription(data['descriptions']))
        dic.update(extractrelation(data['relationships']))
        col.insert(dic)
        if i != 0 and i%100 == 0:
            print(i)
    except:
        print("异常",i)


url = baseUrl + '/browser/' + edition + '/' + version + '/concepts/' + '417850002'
response = urlopen(url).read()
data = json.loads(response.decode('utf-8'))