import requests
import json
import queue
import networkx as nx
import configparser
import os

config_obj = configparser.ConfigParser()
config_obj.read("source/config.ini")


def get_wd_parents(qid):
  relations = ["P31", "P279"]
  S = requests.Session()
  URL = "https://www.wikidata.org/w/api.php"
  PARAMS = {
    "action": "wbgetentities",
    "language": "en",
    "format": "json",
    "ids": qid,
    "limit": 50
  }
  R = S.get(url=URL, params=PARAMS)
  DATA = R.json()

  if "success" in list(DATA.keys()):
    if DATA["success"] != 1:
      print(f"Failed wikidata query -> {DATA}")
      return None
    else:
      parents = []
      claims  = DATA["entities"][qid]["claims"]
      for r in relations:
        claims_list = claims.get(r, None)
        if claims_list:
          parents += [claim["mainsnak"]["datavalue"]["value"]["id"] for claim in claims_list if "datavalue" in claim["mainsnak"]]
      return parents
  else: 
    return None

def get_wd_ontology(qid):
  DG = nx.DiGraph()
  max_depth = 1
  complete  = set([])
  todo      = queue.Queue()
  todo.put((qid, max_depth))
  while not todo.empty():
    (qid,depth) = todo.get()
    if qid in complete or depth==0:
      continue
    DG.add_node(qid)
    parents = get_wd_parents(qid) 
    complete.add(qid)
    if parents:
      for parent in parents:
        DG.add_edge(parent, qid)
        if parent in complete:
          continue
        todo.put((parent, depth-1))
  return DG

def is_legacy(entity):
    
    compatibilityOSKG =  config_obj["kg"]["compatibilityOSKG"]
    with open(compatibilityOSKG, "r") as compatOSKG:
        OSKG    = json.load(compatOSKG)
        legacy  = False
        OS      =  OSKG.get(entity, [])
        legacy  = "z/VSE" in OS
        
    return legacy

def is_open_source(entity):
    open_source_wiki_ids = {"Q341": "free software", "Q131669": "Linux distribution"}
    entitynamesKG = config_obj["kg"]["entitynamesKG"]
    open_source = False
    with open(entitynamesKG, "r") as enKG:
        entities    = json.load(enKG)
        if entity in list(entities.keys()):
          wiki_id = entities[entity]["wiki_id"]
          DG = get_wd_ontology(wiki_id)
          for osid in open_source_wiki_ids:
            if osid in DG.nodes:
              open_source = True
    return open_source

