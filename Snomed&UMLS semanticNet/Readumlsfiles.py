#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 13:38:09 2020

@author: ShihaoYang
"""

import os
import langid
from io import open
import re

from pymongo import MongoClient
from collections import defaultdict
from pymongo.errors import CollectionInvalid
from tqdm import tqdm


PUNCT = re.compile("\W")

LANGDICT = {'ENG': 'en',
            'BAQ': 'eu',
            'CHI': 'zh',
            'CZE': 'cz',
            'DAN': 'dk',
            'DUT': 'nl',
            'EST': 'et',
            'FIN': 'fi',
            'FRE': 'fr',
            'GER': 'de',
            'GRE': 'gr',
            'HEB': 'he',
            'HUN': 'hu',
            'ITA': 'it',
            'JPN': 'jp',
            'KOR': 'ko',
            'LAV': 'lv',
            'NOR': 'no',
            'POL': 'pl',
            'POR': 'po',
            'RUS': 'ru',
            'SPA': 'sp',
            'SWE': 'sw',
            'TUR': 'tr'}

RELATIONMAPPING = {"PAR": 'parent',
                   "CHD": 'child',
                   "RB": 'broader',
                   "RN": 'narrower',
                   "SY": 'synonym',
                   "RO": 'other',
                   "RL": 'similar',
                   "RQ": 'related',
                   "SIB": 'sibling',
                   "AQ": 'qualifier',
                   "QB": 'qualifies',
                   "RU": 'unspecified',
                   "XR": 'notrelated'}

path = r'/Users/emilywang/shihao yang/UMLS/2020AA-full/mmsys/2020AA/2020AA/META'

def createdb(pathtometadir,
             languages=(),
             dbname="umls_all3",
             host="localhost",
             port=27017,
             process_definitions=True,
             process_relations=True,
             process_semantic_types=True,
             process_mrmaps = True,
             preprocessor=lambda x: x,
             overwrite=False):

    client = MongoClient(host=host, port=port)
    db = client.get_database(dbname)

    # Remove any duplicates
    languages = set(languages)

    # Transform non-standard language codings to ISO.
    try:
        {LANGDICT[l.upper()] for l in languages}
    except KeyError:
        raise KeyError("Not all languages you passed are valid.")
    # First create necessary paths, to fail early.
    collection = db.create_collection("term")
    terms = _create_terms(pathtometadir, languages)
    collection.insert_many(terms)
    del(terms)
          
    collection = db.create_collection("string")
    strings,string2concept = _create_strings(pathtometadir, languages)
    collection.insert_many(strings)

    collection = db.create_collection("concept")
    concepts = _create_concepts(pathtometadir,
                                process_definitions,
                                process_relations,
                                process_semantic_types,
                                process_mrmaps,
                                languages,
                                preprocessor,
                                string2concept)
    collection.insert_many(concepts)
    del(concepts)
    return db

def _create_concepts(path,
                     process_definitions,
                     process_relations,
                     process_semantic_types,
                     process_mrmaps,
                     languages,
                     preprocessor,
                     string2concept):
    """
    Read MRCONSO for concepts.
    Parameters
    ----------
    path : string
        The path to the folder containing the MRCONSO file.
    process_definitions : bool
        Whether to process MRDEF, and add definitions to the database.
    process_relations : bool
        Whether to process MRREL, and add relations to the database.
    process_semantic_types : bool
        Whether to process MRSTY, and add semantic types to the database.
    languages : list of str
        The languages to use.
    preprocessor : function
        A function which preprocesses the data.
    Returns
    -------
    concepts : dict
        Dictionary of concept data, to be added to the database.
    """
    
    concepts = defaultdict(dict)

    mrcsonsopath = os.path.join(path, "MRCONSO.RRF")

    for idx, _ in enumerate(open(mrcsonsopath)):
        pass

    num_lines = idx
    
    totalcui = []
    for record in tqdm(open(mrcsonsopath), total=num_lines):
        split = record.strip().split("|")
        cui = split[0]
        totalcui.append(cui)
    
    print("Reading MRCONSO for concepts.")
    for record in tqdm(open(mrcsonsopath), total=num_lines):
        split = record.strip().split("|")

        if languages and split[1] not in languages:
            continue

        cui = split[0]
        sui = split[5]
        lui = split[3]
        

        c = concepts[cui]
        
        if "one_of_name" not in c:
            c["one_of_name"] = string2concept[sui]["string"]

        c["_id"] = cui

        if split[2] == "P":
            c["preferred"] = lui

        try:
            c["lui"].add(lui)
        except KeyError:
            c["lui"] = set([lui])
        try:
            c["sui"].add(sui)
        except KeyError:
            c["sui"] = set([sui])
            

    if process_definitions:
        concepts = process_mrdef(path, concepts, languages, preprocessor)
    if process_relations:
        concepts = process_mrrel(path, concepts,totalcui)
    if process_semantic_types:
        concepts = process_mrsty(path, concepts)
    if process_mrmaps:
        concepts = process_mrmap(path, concepts)
    for v in concepts.values():
        try:
            v['lui'] = list(set(v['lui']))
        except KeyError:
            pass
        try:
            v['sui'] = list(set(v['sui']))
        except KeyError:
            pass

    return list(concepts.values())

def _create_terms(path, languages):
    """Read MRCONSO for terms."""
    terms = defaultdict(dict)
    mrcsonsopath = os.path.join(path, "MRCONSO.RRF")
    for idx, _ in enumerate(open(mrcsonsopath)):
        pass

    num_lines = idx
    print("Reading MRCONSO for terms.")
    for record in tqdm(open(mrcsonsopath), total=num_lines):

        split = record.strip().split("|")

        if languages and split[1] not in languages:
            continue

        cui = split[0]
        sui = split[5]
        lui = split[3]

        t = terms[lui]

        t["_id"] = lui
        try:
            t["cui"].append(cui)
        except KeyError:
            t["cui"] = [cui]
        try:
            t["sui"].append(sui)
        except KeyError:
            t["sui"] = [sui]

    for v in terms.values():
        v["sui"] = list(set(v["sui"]))
        v["cui"] = list(set(v["cui"]))
        if len(v["cui"]) == 1:
            v["cui"] = v["cui"][0]

    return list(terms.values())

#terms = _create_terms(path,['ENG'])

def _create_strings(path, languages):
    """Read MRCONSO for strings."""
    strings = defaultdict(dict)

    mrcsonsopath = os.path.join(path, "MRCONSO.RRF")

    for idx, _ in enumerate(open(mrcsonsopath)):
        pass

    num_lines = idx

    print("Reading MRCONSO for strings.")
    for record in tqdm(open(mrcsonsopath), total=num_lines):

        split = record.strip().split("|")
        string = split[14]

        # Check BSON length
        byte_string = string.encode("utf-8")
        if len(byte_string) >= 1000:
            # Truncate 1000 bytes
            string = byte_string[:1000].decode('utf-8')

        if languages and split[1] not in languages:
            continue

        cui = split[0]
        sui = split[5]
        lui = split[3]

        # Create lexical representation.
        tokenized = " ".join(PUNCT.sub(" ", string).split())

        s = strings[sui]

        s["_id"] = sui
        s["string"] = string
        s["lower"] = string.lower()
        s["tokenized"] = tokenized
        s["lang"] = split[1]
        s["numwords"] = len(string.split())
        s["numwordslower"] = len(tokenized.split())
        s["lui"] = lui
        s["cui"] = cui

    return list(strings.values()),strings

#strings = _create_strings(path,['ENG'])

def process_mrrel(path, concepts,totalcui):
    """
    Read the relations from MRREL.RRF, and add them to concepts.
    Because bidirectional relations in UMLS occur for both directions,
    only the direction which occurs in the UMLS is added.
    """
    mrrelpath = os.path.join(path, "MRREL.RRF")

    for idx, _ in enumerate(open(mrrelpath)):
        pass

    num_lines = idx

    print("Reading MRREL.RRF for relations.")
    for record in tqdm(open(mrrelpath), total=num_lines):

        split = record.strip().split("|")

        cui = split[4]
        dest = split[0]
        if dest not in totalcui:
            continue
        # provide dictionary mapping for REL
        rel = RELATIONMAPPING[split[3]]
        if rel == 'other' and split[7] != '':
            rel = split[7]
            
        c = concepts[cui]
        c["rel"] = c.get("rel", {})

        try:
            concepts[cui]["rel"][rel].add(dest)
        except KeyError:
            concepts[cui]["rel"][rel] = set([dest])

    for v in concepts.values():
        try:
            for reltype in v["rel"]:
                v["rel"][reltype] = list(v["rel"][reltype])
        except KeyError:
            pass

    return concepts


def process_mrdef(path,
                  concepts,
                  languages,
                  preprocessor):
    """
    Read definitions from MRDEF.RRF.
    We append this to the intermediate dictionary (concepts), not the DB
    because this is way faster.
    Parameters
    ----------
    path : string
        The path to the META dir.
    concepts : dict
        The dictionary of concepts to which to add the definitions.
    languages : list of str
        The languages to use.
    preprocessor : function
        Function that preprocesses the defintions. Should be a function which
        takes a string as input and returns a string.
    Returns
    -------
    concepts : dict
        The updated concept dictionary with added definitions.
    """
    isolanguages = {LANGDICT[l.upper()] for l in languages}
    print(isolanguages)

    mrdefpath = os.path.join(path, "MRDEF.RRF")

    for idx, _ in enumerate(open(mrdefpath)):
        pass

    num_lines = idx

    print("Reading MRDEF.RRF for definitions.")
    for record in tqdm(open(mrdefpath), total=num_lines):
        split = record.strip().split("|")

        cui = split[0]
        c = concepts[cui]
        definition = split[5]

        # Detect language -> UMLS does not take into account language
        # in MRDEF.
        lang, _ = langid.classify(definition)
        if lang not in isolanguages:
            continue

        # Tokenize the definition.
        if preprocessor:
            definition = preprocessor(definition)
        try:
            c["definition"].append(definition)
        except KeyError:
            c["definition"] = [definition]

    return concepts


def process_mrsty(path, concepts):
    """Read semantic types from MRSTY.RRF."""
    mrstypath = os.path.join(path, "MRSTY.RRF")

    for idx, _ in enumerate(open(mrstypath)):
        pass

    num_lines = idx

    print("Reading MRSTY.RRF for semantic types.")
    for record in tqdm(open(mrstypath), total=num_lines):
        split = record.strip().split("|")

        cui = split[0]
        if cui not in concepts:
            continue
        c = concepts[cui]
        semantic_type = split[3]
        try:
            c["semtype"].append(semantic_type)
        except KeyError:
            c["semtype"] = [semantic_type]

    return concepts

def process_mrmap(path, concepts):
    """Read semantic types from MRMAP.RRF."""
    mrmappath = os.path.join(path, "MRMAP.RRF")

    for idx, _ in enumerate(open(mrmappath)):
        pass

    num_lines = idx

    print("Reading MRMAP.RRF & MRSMAP.RRF")
    for record in tqdm(open(mrmappath), total=num_lines):
        split = record.strip().split("|")

        cui = split[6]
        if cui not in concepts:
            continue
        c = concepts[cui]
        c["map_type"] = {}
        rel = RELATIONMAPPING[split[12]]
        map_type = split[16]
        rule = re.compile(r'[<](.*?)[>]', re.S)
        mapr = re.findall(rule, map_type)
        try:
            c["map_type"][rel].extend(mapr)
        except KeyError:
            c["map_type"][rel] = mapr
            
    mrsmappath = os.path.join(path, "MRSMAP.RRF")
    for idx, _ in enumerate(open(mrsmappath)):
        pass
    num_lines = idx
       
    for record in tqdm(open(mrsmappath), total=num_lines):
        split = record.strip().split("|")
        cui = split[4]
        if cui not in concepts:
            continue
        c = concepts[cui]
        rel = RELATIONMAPPING[split[6]]
        map_type = split[8]
        rule = re.compile(r'[<](.*?)[>]', re.S)
        mapr = re.findall(rule, map_type)
        if "map_type" not in c:
            c["map_type"] = {}
        try:
            c["map_type"][rel].extend(mapr)
        except KeyError:
            c["map_type"][rel] = mapr
        c["map_type"][rel] = list(set(c["map_type"][rel]))
        
    return concepts

db = createdb(path,['ENG'])