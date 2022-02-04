
# Add new images
#
# 1. Generate new image list
#     1. List new images
#     2. Extract Container name, OS, tech tokens(lang, lib, App, Appserver, plugin, runlib, runtime), Docker_URL, CertofImageAndPublisher
#     3. Entity standardization for OS and tech entities
#     4. If entities are standardized:
#         1. Put the results to  [lang, lib, App, Appserver, plugin, runlib, runtime] column
#     5. Else
#         1. Add new entities
#     6. given unknown or new entity, determine it status : COTS , Legacy , Open source , and container image

from datetime import datetime
import csv
import sqlite3
from sqlite3 import Error
from networkx.generators.random_graphs import fast_gnp_random_graph
import xlrd
from xlrd import xlsx
from  xlutils.copy import copy
from xlrd import open_workbook

from source import url_detector
from source import data_loader
from source.opensource_legacy import is_legacy, is_open_source

class DB_Connect:
    def __init__(self):
        pass

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print("DB is connected")
        except Error as e:
            print(e)

        return conn
    
    def get_entity_type(self, conn, techtokens):
        cur = conn.cursor()

        for tokens in techtokens:
            container_name = tuple([0])
            #os = tuple[1]
            os = 'Linux'
            lang = tuple([2])
            lib = tuple([3])
            app = tuple([4])
            app_server = tuple([5])
            plugin = tuple([6])
            runlib = tuple([7])
            runtime = tuple([8])
            Operator_Correspondent_Image_URL = tuple([9])
            operator_repository = tuple([10])
            other_operators = tuple([11])


            #print(child_class)
            os_id = None
            if os:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+os+"'")
                result = cur.fetchone()

                if result:
                    os_id = result[0]

                else:
                    print("invalid os:"+str(os))

            lang_id = None
            if lang:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+lang+"'")
                result = cur.fetchone()

                if result:
                    lang_id = result[0]

                else:
                    print("invalid lang:"+str(lang))

            lib_id = None
            if lib:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+lib+"'")
                result = cur.fetchone()

                if result:
                    lib_id = result[0]

                else:
                    print("invalid lib:"+str(lib))

            app_id = None
            if app:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+app+"'")
                result = cur.fetchone()

                if result:
                    app_id = result[0]

                else:
                    print("invalid lib:"+str(app))

            app_server_id = None
            if app_server:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+app_server+"'")
                result = cur.fetchone()

                if result:
                    app_server_id = result[0]

                else:
                    print("invalid lib:"+str(app_server))

            plugin_id = None
            if plugin:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+plugin+"'")
                result = cur.fetchone()

                if result:
                    plugin_id = result[0]

                else:
                    print("invalid lib:"+str(plugin))

            runlib_id = None
            if runlib:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+runlib+"'")
                result = cur.fetchone()

                if result:
                    runlib_id = result[0]

                else:
                    print("invalid lib:"+str(runlib))

            runtime_id = None
            if runtime:
                cur.execute("SELECT id FROM entities WHERE entity_name='"+runtime+"'")
                result = cur.fetchone()

                if result:
                    runtime_id = result[0]

                else:
                    print("invalid lib:"+str(runtime))

            if  os_id:
                cur.execute(sql, (container_name, os_id, lang_id, lib_id, app_id, app_server_id, plugin_id, runlib_id, runtime_id, Operator_Correspondent_Image_URL, operator_repository, other_operators))

        conn.commit()
        return cur.lastrowid


def  save_to_xls_file(all_entities):

        
    entity_data = open_workbook("kb/entity_data.xlsx")
    book = copy(entity_data)  # creates a writeable copy

    entities = book.get_sheet(0)  # get a first sheet
    max_row = len(entities.get_rows())

      
    for rowx in range(1 ,max_row):
        
        # Write the data to rox, column
        
        row_data = all_entities[rowx-1]

        entities.write(rowx, 5, row_data["COTS"] )
        entities.write(rowx, 7, row_data["Container image"])
        entities.write(rowx ,6 , row_data["Legacy"])
        entities.write(rowx ,8 , row_data["Open Source"])

    book.save("kb/entity_data_new.xls")


def entity_index_mapper(catalogue_images:dict) :
    dockerhub_mapper_indexes , openshift_mapper_indexes , operator_mapper_indexes = [] , [] , []
    dockerhub_indexes , openshift_indexes , operator_indexes = [] ,[] ,[]

    for catalogue_name, catalogue_data in catalogue_images.items():
        for image in catalogue_data:
            if  catalogue_name == "docker_images":
                index = [image[key] for key in list(image.keys())[1:]  if image[key] ]
                dockerhub_mapper_indexes.append(index)
            elif catalogue_name == "openshift_images":
                index = [image[key] for key in list(image.keys())[1:]  if image[key] ]
                openshift_mapper_indexes.append(index)
            elif catalogue_name =="operator_images": 
                index = [image[key] for key in list(image.keys())[1:]  if image[key] ]
                operator_mapper_indexes.append(index)
            else: continue


    for indexes in dockerhub_mapper_indexes:
        for idx in indexes:
            dockerhub_indexes.append(idx)

               
    for indexes in openshift_mapper_indexes:
        for idx in indexes:
            openshift_indexes.append(idx)


    for indexes in operator_mapper_indexes:
        for idx in indexes:
            operator_indexes.append(idx)
    
    return dockerhub_indexes ,openshift_indexes , operator_indexes

def has_docker_images(entity,doc):
   
    print("DOCKERHUB CONTAINER IMAGES\n")
    input_data = {"entity name": entity}   
    docker_images = doc.search_result(input_data)

    print("docker images {} ".format(docker_images))

    if docker_images[list(docker_images.keys())[0]]['Windows base os'] =='NA' and docker_images[list(docker_images.keys())[0]]['linux base os'] =='NA': return False
    else: return True

def has_openshift_image(entity,openshift_instance):

    print("OPENSHIFT CONTAINER IMAGES\n")
    input_data = {"entity name": entity}   
    openshift_images = openshift_instance.search_redhat_containers(input_data["entity name"])

    if openshift_images: return True
    else: return False


def has_operator_image(entity,opr):

    print("OPERATORS\n")
    input_data = {"entity name": entity}   
    operators = opr.search_operator(input_data["entity name"])

    if operators: return True
    else: return False


def generate_app_status( ):
    """  
    Given an entity name , determine the following entity's status: COTS, Legacy status(Yes or No) , Container image(Yes or No)
    Open Source (Yes or No)

    Keyword arguments: None
    argument: None
    Return: None : Save results to spreadsheet 
    """
    
    excel_file_path = "kb/entity_data.xlsx"
    entities_struct = {"id": 1, "name": "", "COTS":"" , "Legacy": "", "Container image":
           "" , "Open Source": " "}

    all_entities = []
    doc = url_detector.DockerHub("https://hub.docker.com/")
    openshift_instance = url_detector.Openshift("https://catalog.redhat.com/software/containers/search")
    opr =url_detector.OpenShiftOperator("https://operatorhub.io/")

    sheets = {"docker_images": [] , "openshift_images": [] ,"operator_images": []}
    
    for   key , _ in sheets.items(): 
        sheets[key] = data_loader.load_images(excel_file_path,sheetname=key)
    
    dockerhub_indexes , openshift_indexes , operator_indexes = entity_index_mapper(sheets)
    entities = data_loader.load_entity(excel_file_path,sheetname="entities")

    for idx, entity_name in entities.items():
        entity_sample = entities_struct.copy()
        entity_sample["name"] = entity_name
        entity_sample["id"] = int(idx)

        if idx in dockerhub_indexes or idx in openshift_indexes or idx in operator_indexes :
            print("{}: {} is not a COTS ".format(idx, entity_name))
            entity_sample["COTS"] = "N"
            entity_sample["Container image"] = "Y"
            if is_legacy(entity_name):  entity_sample["Legacy"] = "Y"
            else: entity_sample["Legacy"] = "N"
            if is_open_source(entity_name): entity_sample["Open Source"] = "Y"
            else: entity_sample["Open Source"] = "N"

        else:
            
            #check images from providers: dockerhub , openshift(RedHat) , and operatorhub.io

            print("{}: {} has no standardized entity. let find possible images".format(idx, entity_name))

            if has_docker_images(entity_name,doc):

                entity_sample["COTS"] = "N*"
                entity_sample["Container image"] = "Y*"
                if is_legacy(entity_name):  entity_sample["Legacy"] = "Y"
                else: entity_sample["Legacy"] = "N"
                if is_open_source(entity_name): entity_sample["Open Source"] = "Y"
                else: entity_sample["Open Source"] = "N"

            elif has_openshift_image(entity_name, openshift_instance):
                entity_sample["COTS"] = "N*"
                entity_sample["Container image"] = "Y*"
                if is_legacy(entity_name):  entity_sample["Legacy"] = "Y"
                else: entity_sample["Legacy"] = "N"
                if is_open_source(entity_name): entity_sample["Open Source"] = "Y"
                else: entity_sample["Open Source"] = "N"

            elif has_operator_image(entity_name,opr):
                entity_sample["COTS"] = "N*"
                entity_sample["Container image"] = "Y*"
                if is_legacy(entity_name):  entity_sample["Legacy"] = "Y"
                else: entity_sample["Legacy"] = "N"
                if is_open_source(entity_name): entity_sample["Open Source"] = "Y"
                else: entity_sample["Open Source"] = "N"

            else: 
                entity_sample["COTS"] = "Y"
                entity_sample["Container image"] = "N"
                if is_legacy(entity_name):  entity_sample["Legacy"] = "Y"
                else: entity_sample["Legacy"] = "N"
                if is_open_source(entity_name): entity_sample["Open Source"] = "Y"
                else: entity_sample["Open Source"] = "N"


        all_entities.append(entity_sample)

    save_to_xls_file(all_entities)



if __name__ == '__main__':

    # generate app status
    generate_app_status()
    

    # TODO: Switch catalog [DockerHub, Openshift and OperatorHub]
    # Import list of images or generate an image list from catalog
    
    # with open('kb/DockerHubImages.csv') as f:
    #     reader = csv.reader(f)
    #     images = [row[1] for row in reader]
    #     images = images[1:]

    # Extract required information for image table
    # Container name, OS, tech tokens(lang, lib, App, Appserver, plugin, runlib, runtime), Docker_URL and CertofImageAndPublisher
   
    # output = {}

    #Load existing kg
    # db_inst = DB_Connect()
    # db_conn = None
   # db_conn = db_inst.create_connection(file_path)
    
    # if db_conn is not None:
    #     print('')
    
    # if db_conn:
    #     db_conn.close()
    #     print("Exiting DB")

    #Entity standardization for OS and tech entities
