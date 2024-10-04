from crawl.src.categorie_get_all_firms_urls import *
from  crawl.src.firm_get_firm_infos import *
from crawl.src.common import *

def categorie_get_all_firms_infos(categorie = None, use_delay = True, extension="json"):
    if categorie != None:
        CATEGORIE = categorie
        CATEGORIE_URI = SITE_URI + "/categories/" + CATEGORIE

    print("Get Firms Urls from categorie")
    firm_urls = categorie_get_all_firms_urls(CATEGORIE_URI, use_delay)

    print("Get Firms Infos")
    firms_infos = firm_getFirmInfo(firm_urls, use_delay)

    print("Write File")
    file_name = CATEGORIE + "_all_firms_infos"
    to_file(firms_infos, file_name, extension=extension, folder)


# #########################################
# LANCEMENT SCRIPT
USE_DELAY = True
CATEGORIE = "investments_wealth"
categorie_get_all_firms_infos(CATEGORIE, USE_DELAY)

#################################################"
# MAIN

