from firm_get_firm_infos import *
from categorie_get_all_firms_urls import categorie_get_all_firms_urls

#################################################"
# MAIN

USE_DELAY = False

def categorie_get_all_firms_infos(categorie = None, extension="json"):
    """
    Recupere toutes les firmInfos d'une categorie et cree un fichier json.
    Traitement long, eviter de l'executer sur la VM
    @param: categorie a traiter
    @param: extension de sortie
    """
    if categorie != None:
        CATEGORIE = categorie
        CATEGORIE_URI = SITE_URI + "/categories/" + CATEGORIE
    
    firm_urls = categorie_get_all_firms_urls(CATEGORIE_URI)
    firms_infos = firm_getFirmInfo(firm_urls)

    name = CATEGORIE + "_all_firms_infos"
    to_file(firms_infos, name, extension=extension, folder)


    print("stop")