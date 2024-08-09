from bs4 import BeautifulSoup as bs
import json

import time
import random
import csv
import os
import shutil

from common import *
from firm_get_onePage_reviews import firm_get_onePage_reviews

def getAllFirmReviewToJson(firm_url, output_folder, extension):
    """
    Crée un fichier json pour chaque page de reviews d'une firme
    format du Json: voir firm_getFirmReviews
    :param firm_url: url de la page de la firme
    :param filepath_out: str chemin du dossier de sortie
    :return: void
    """

    # #########################
    # ATTENTION: VARIABLE DE DEV USE_DELAY
    # j'utilise cette variable pour faire sauter la gestion de l'erreur 403 et le delay de 3 secondes.
    # ca permet d'eviter que le test sur un petit jeu de données attende 3s entre chaques appels.
    # TODO plus tard: Regler le delais en fonction du nombre de page a recuperer

    USE_DELAY = True

    print("getAllFirmReviewToJson - START")
    """
    url_in_error=[
        ("https://www.trustpilot.com/review/turbodebt.com?page=202","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=210","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=232","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=284","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=364","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=470","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=533","500"),
        ("https://www.trustpilot.com/review/turbodebt.com?page=549","500")
    ]
    """
    


    # TEST ERREURs: ON SKIPPE lae for

    # recupere le nombre de page
    soup = getPageSoup(firm_url, use_delay=USE_DELAY)

    if type(soup) is tuple: # erreur HTML != 200
        raise Exception("getAllFirmReviewToJson - Error on first connect, please check", soup[0], soup[1])
    else:
        # Recherche la derniere page, Exception si pagination absente
        last_page = getLastPage(soup)

        url_in_error = []

        for i in range(1, last_page + 1):
            # create URL
            if i == 1:  # page 1 url sans ?page=i
                url = firm_url
            else:
                url = firm_url + "/?page=" + str(i)

            print(url)

            # plus utile use_delay dans getSoup
            if USE_DELAY:
                # DELAY FIXE + DELAY RANDOM (on ne wait pas pour la 1ere page)
                random_delay = random.random()
                time.sleep(DELAY_PER_PAGE_SECONDS + random_delay)

                            # Request TrustPilot
            page_soup = getPageSoup(url, use_delay=USE_DELAY)

            # RETOUR HTML & WAIT
            # si on tombe sur une erreur 403:
            # on attend 2 minutes, on retente la page:
            #       si error: on place la page dans la liste d'erreur et on passe a la suivante
            #       sinon: la page continue dans le process normal
            if type(page_soup) is tuple: # erreur HTML
                # Save in url_in_error
                if page_soup[1] == 403: # WE ARE SPOTTED !! TAKE COVER
                    if USE_DELAY:
                        print("getAllFirmReviewToJson - Error 403 - WAIT ", DELAY_TIME, "seconds START"  )
                        time.sleep(DELAY_TIME)
                        page_soup = getPageSoup(url, use_delay=USE_DELAY)

                    if type(page_soup) is tuple: # Page encore en erreur: on l'ajoute aux erreur pour traitement ulterieur et on passe a l'iteration suivante
                        print("Still in error: put in url_in_error")
                        url_in_error.append(page_soup)
                        continue
                    else:
                        print("[ERROR]", page_soup)
                        url_in_error.append(page_soup)
                        continue
                else:
                    print("[ERROR]", page_soup)
                    url_in_error.append(page_soup)
                    continue

            # PAGE OK: code HTML 200
            # execution function de crawl
            page_reviews = {"page": i, "data": firm_get_onePage_reviews(page_soup, url)}

            # FileName
            if "?page=" in url:
                firm_id = url.split("/")[-2]
            else:
                firm_id = url.split("/")[-1]
            
            page_number = i

            if page_number is None:
                page_str = ""
            else:
                # On ajoute des 0 devant les numero de pages pour le tri
                page_str = str(page_number)
                while len(page_str) < 4:
                    page_str = "0" + page_str

            filename = "firm_reviews" + "_" + firm_id + "_" + str(page_str)



            # ecriture json
            to_file(page_reviews,  filename, folder=output_folder, extension=extension)

        # POUR TEST CREATE FAUSSES ERREURS

        # Traitement des erreurs
    if len(url_in_error) == 0:
        print("NO ERROR")
    else:
        print ("RETRY URL IN ERROR")
        still_in_error = []
        for err in url_in_error:
            print(str(err))

            # FileName
            if "?page=" in err[0]:
                tmp_split = err[0].split("?page=")
                firm_id = tmp_split[0].split("/")[-1]
                page_number = int(tmp_split[-1])
            else:
                firm_id = err[0].split("/")[-1]
                page_number = 1

            soup = getPageSoup(err[0], use_delay=USE_DELAY)
            if type(soup) is tuple:
                print ("STILL IN ERROR: Manual check needed")
                still_in_error.append(err)
            else:
                page_reviews = {"page": page_number, "data": firm_get_onePage_reviews(soup, err[0])}

                # On ajoute des 0 devant les numero de pages pour le tri
                page_str = str(page_number)
                while len(page_str) < 4:
                    page_str = "0" + page_str

                filename = "firm_reviews" + "_" + firm_id + "_" + str(page_str)

                # ecriture json
                to_file(page_reviews,  filename, folder=output_folder, extension=extension)
                print ("CORRECTED")
                
        print("RECAP RETRY")
        if len(still_in_error)==0: print("Aucune erreur restante")
        else:
            for x in still_in_error: 
                print("Reprise manuelle nescessaire")
                print(x)





#################################################"
# MAIN

# INIT WORKING FOLDER
# Pour resoudre un probleme avec le debug VSCode on fixe le dossier actif explicitement
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Cas de test
#FIRM = "egcu.org"

# Cas reel
FIRM = "turbodebt.com"

FIRM_URI = SITE_URI +"/review/"+ FIRM


# CREATION DOSSIER
folder_file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + "_" + FIRM + "_reviews"
tmp_path = os.path.join(TEMP_FOLDER, folder_file_name)
os.makedirs(tmp_path)


# GENERATION DES FICHIERS DANS DOSSIER TEMP

print("#######################################")
print("Generation des fichiers Reviews")
print("Firms",FIRM_URI)
print("TEMP_FOLDER",TEMP_FOLDER)

getAllFirmReviewToJson(FIRM_URI, tmp_path, extension="json")

print("#######################################")
print("Aggregation")
print("INPUT_FOLDER", tmp_path)
print("OUTPUT_FOLDER", OUTPUT_FOLDER)
print("file_name", folder_file_name)

# Aggregation des fichiers
fileAggregation(tmp_path, OUTPUT_FOLDER, folder_file_name, json_output=True, csv_output=True)


# Verification
# TODO

# Effacement du dossier temp
print("#######################################")
print("Suppresion du dossier temp")
shutil.rmtree(tmp_path)


