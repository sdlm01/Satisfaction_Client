from src.categorie_get_all_firms_urls import *
from  src.firm_get_firm_infos import *
from src.common import *
import datetime as dt

def categorie_get_firms_infos(firm_list, use_delay = True, extension="json"):
    """
    Cree un fichier contenant les firms info dans le folder common.FOLDER_OUT
    :param list_firm: list des id de firm
    :param use_delay: defaut True utilise les delay entre chaques appels
    :param extension: defaut json extension du fichier de sortie
    :return: list of dict firm info (see: src.firm_get_firm_infos.firm_get_oneFirm_infos)
    """
    print("Get Firms Infos")
    firms_infos = firm_getFirmInfo(firm_list, use_delay)

    print("Write File")

    file_name = dt.datetime.today().strftime("%Y-%m-%d") + "_update_firms_infos"
    to_file(firms_infos, file_name, extension=extension, folder=OUTPUT_FOLDER)


# #########################################
# LANCEMENT SCRIPT
USE_DELAY = True
def getFirmList():
    f = open("conf//firms.properties", "r")
    lst = f.readlines()
    return [x.replace("\n", "") for x in lst]
categorie_get_firms_infos(getFirmList(), extension="csv")

#################################################"
# MAIN

