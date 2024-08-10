from categorie_get_all_firms_urls import *
from firm_get_firm_infos import *
from common import *

def categorie_get_all_firms_infos(categorie = None, use_delay = True, extension="json"):
    if categorie != None:
        CATEGORIE = categorie
        CATEGORIE_URI = SITE_URI + "/categories/" + CATEGORIE

    print("Get Firms Urls from categorie")
    firm_urls = categorie_get_all_firms_urls(CATEGORIE_URI, use_delay)

    print("Get Firms Infos")
    firms_infos = firm_getFirmInfo(firm_urls)

    print("Write File")
    file_name = CATEGORIE + "_all_firms_infos"
    to_file(firms_infos, file_name, extension=extension, folder=OUTPUT_FOLDER)


# #########################################
# LANCEMENT SCRIPT
USE_DELAY = False
CATEGORIE = "atm"
categorie_get_all_firms_infos(CATEGORIE, USE_DELAY)

#################################################"
# MAIN

