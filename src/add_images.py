
from datetime import datetime
import csv
import sqlite3
from sqlite3 import Error
from networkx.generators.random_graphs import fast_gnp_random_graph
import xlrd
from xlrd import xlsx
from  xlutils.copy import copy
from xlrd import open_workbook
import data_loader


def entity_index_mapper(catalogue_images:dict) :
    dockerhub_mapper_indexes , openshift_mapper_indexes , operator_mapper_indexes = [] , [] , []
    dockerhub_indexes , openshift_indexes , operator_indexes = [] ,[] ,[]

    for catalogue_name, catalogue_data in catalogue_images.items():
        for image in catalogue_data:
            if  catalogue_name == "docker_images":
                index = [image[key] for key in list(image.keys())[1:]  if image[key] ]
                dockerhub_mapper_indexes.append(index)
            else: continue

    for indexes in dockerhub_mapper_indexes:
        for idx in indexes:
            dockerhub_indexes.append(idx)    
    
    return dockerhub_indexes


def load_entities( ):
   
    excel_file_path = "kb/entity_data.xlsx"
    all_entities = []
    sheets = {"docker_images": [] }
    for   key , _ in sheets.items(): 
        sheets[key] = data_loader.load_images(excel_file_path,sheetname=key)
    
    dockerhub_indexes = entity_index_mapper(sheets)
    entities = data_loader.load_entity(excel_file_path,sheetname="entities")

    for idx, entity_name in entities.items():
        all_entities.append(entity_name)
    return all_entities

# 'https://registry.hub.docker.com/v2/repositories/library/fedora/tags/'
if __name__ == '__main__':
    # load entities from kb 
    print(load_entities())
    
