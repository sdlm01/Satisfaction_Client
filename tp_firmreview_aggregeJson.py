from bs4 import BeautifulSoup as bs
import requests
import json
import datetime
import time
import random
import csv
from os import listdir
from os.path import isfile, join

def to_json_file(dict, filepath):
    """
    dump le dict dans un fichier Json
    :param dict: dictionnary
    :param url: output filepath
    :return: write dict to jsonFile
    """
    with open(filepath, 'w') as file:
        file.write(json.dumps(dict, indent=4, separators=(',', ': ')))

def getJsonName(page_url, page_number=None):
    """
        Retourne le nom du fichier output
        :param page_url: str
        :param page_number: str
        :return: str: date YYYYMMDD-HHMi _firmReviewPage_ firm_id _ numero de page .json
    """
    if "?page=" in page_url:
        firm_id = page_url.split("/")[-2]
    else:
        firm_id = page_url.split("/")[-1]

    today = datetime.datetime.now()
    if page_number is None:
        page_str = ""
    else:
        # On ajoute des 0 devant les numero de pages pour le tri
        page_str = str(page_number)
        while len(page_str) < 4:
            page_str = "0"+page_str

    return today.strftime("%Y%m%d-%H-%M") + "_firmReviewPage" + "_" + firm_id + "_" + str(page_str) +  ".json"

def fileAggregation(folder_path, firm_id, json_output=True, csv_output=False):
    # recupere tous les fichiers du dossier
    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    # filtre sur la firm_id
    firm_file = []
    for file in files:
        if firm_id in file:
            firm_file.append(file)
    # ordonne le tableau pour faciliter le comptage des pages
    firm_file.sort()

    # creer fichier final
    final_file = []
    last_page = 0
    suivi_page = []
    reviews_count = 0
    file_count = len(firm_file)
    err_sequence = []

    # création de fichier CSV en l'en-tête
    if csv_output:
        csv_filepath = join(folder_path, f"all_reviews_{firm_id}.csv")
        csv_file = open(csv_filepath, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_header = ["firm_url", "firm_name", "review_url", "review_title", "note", "reponse", "author_name", "author_url", "author_localisation", "review_date", "experience_date"]
        csv_writer.writerow(csv_header)

    if json_output or csv_output:
        for page_url in firm_file:
            file = open(join(folder_path, page_url),'r', encoding='utf-8')
            data = json.load(file)

            try:
                tmp = data["page"]
            except:
                raise Exception("Le fichier n'a pas le format attendu, verifier les fichiers d'entrée, il y a un intru: "+page_url)

            # controle la sequence des pages
            if last_page != int(data["page"]) - 1:
                print("ERREUR dans la sequence des pages entre", last_page, "et", data["page"])
                err_sequence.append(int(data["page"]))

            # Pour suivi
            suivi_page.append(int(data["page"]))
            last_page = int(data["page"])
            reviews_count += len(data["reviews"])

            # Ajout a final list
            final_file += data["reviews"]

            # Écrire les données dans le fichier CSV
            if csv_output:
                for review in data["reviews"]:
                    csv_writer.writerow([review.get("firm_url"), review.get("firm_name"), review.get("review_url"),
                                         review.get("review_title"), review.get("note"), review.get("reponse"),
                                         review.get("author_name"), review.get("author_url"), review.get("author_localisation"),
                                         review.get("review_date"), review.get("experience_date")])

            print("page", data["page"], "saved in memory")

        # Fermeture du fichier CSV
        if csv_output:
            csv_file.close()

        print("Bilan aggregation")
        print("file count", file_count)
        print("reviews count", reviews_count)

        if json_output:
            print("write final file")
            to_json_file(final_file, folder_path + "all_reviews_"+firm_id+".json")


#################################################"
# MAIN
SITE_URI="https://www.trustpilot.com"
# Firms Reviews
TEST_FIRM_URI = SITE_URI + "/review/egcu.org"
#TEST_FIRM_REVIEW_OUTPUT_FILE = "C:\\tmp\\firm_EGCU_Reviews.json"

FIRM_URI = SITE_URI + "/review/turbodebt.com"
#FIRM_REVIEW_OUTPUT_FILE = "C:\\tmp\\firm_TurboDebt_Reviews.json"

OUTPUT_FOLDER = "C:\\tmp\\"

fileAggregation(OUTPUT_FOLDER, "turbodebt.com", json_output=False, csv_output=True)




