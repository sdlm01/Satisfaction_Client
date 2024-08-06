from bs4 import BeautifulSoup as bs

import datetime
import time
import random
import csv
from os import listdir
from os.path import isfile, join

from common import *
from categorie_get_all_firms_urls import *
from firm_get_firm_infos import *




#################################################"
# MAIN

def categorie_get_all_firms_infos(categorie = None, extension="json"):
    CATEGORIE = "atm"
    CATEGORIE_URI = SITE_URI + "/categories/" + CATEGORIE

    if categorie != None:
        CATEGORIE = categorie
        CATEGORIE_URI = SITE_URI + "/categories/" + CATEGORIE
    
    firm_urls = categorie_get_all_firms_urls(CATEGORIE_URI)
    firms_infos = firm_getFirmInfo(firm_urls)

    name = CATEGORIE + "_all_firms_infos"
    to_file(firms_infos, name, extension=extension, folder=OUTPUT_FOLDER)


    print("stop")
    


# #########################################
# LANCEMENT SCRIPT

categorie_get_all_firms_infos()