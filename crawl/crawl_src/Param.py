import json
import os

class Param(object):
  def __new__(cls, PARAM_FOLDER, PARAM_FILE_JSON):
    if not hasattr(cls, 'instance'):
      cls.instance = super(Param, cls).__new__(cls)
    return cls.instance
  
  def __init__(self, PARAM_FOLDER, PARAM_FILE_JSON):
    # Pour container, recuperer la variable d'env chemin de la conf.
    with open(os.path.join(PARAM_FOLDER, PARAM_FILE_JSON), "r") as file:
      conf = json.load(file)
    
    print("Parameters", conf)

    self.SITE_URI = conf["SITE_URI"]
    self.OUTPUT_FOLDER = conf["OUTPUT_FOLDER_CONTAINER"]
    self.TEMP_FOLDER = conf["TEMP_FOLDER_CONTAINER"]
    self.LOG_FOLDER = conf["LOG_FOLDER_CONTAINER"]

    self.MONGO_DB_HOST = conf["MONGO_DB_HOST"] 
    self.MONGO_DB_PORT = conf["MONGO_DB_PORT"]
    self.MONGO_DB_USERNAME = conf["MONGO_DB_USERNAME"] 
    self.MONGO_DB_PASSWORD = conf["MONGO_DB_PASSWORD"]

    self.DELAY_PER_PAGE_SECONDS = conf["DELAY_PER_PAGE_SECONDS"]
    self.DELAY_WHEN_403 = conf["DELAY_WHEN_403"]


    print(self.OUTPUT_FOLDER)



    
    
