import datetime
from bs4 import BeautifulSoup as bs
import random
import csv
import requests
import json
import time
import os

# GET PARAMETERS FROM CONF FILE
#f = open(os.path.join("conf", "firms.properties"), "r")
#f.readlines()

# SITE_URI = "https://www.trustpilot.com/"
# OUTPUT_FOLDER = "/app/src/out/"
# TEMP_FOLDER = "/app/src/temp/"
# CONF_FOLDER = "/app/src/conf/"

DELAY_PER_PAGE_SECONDS = 2
DELAY_TIME = 160

JSON_OUTPUT= True
CSV_OUTPUT= False

def to_json_file(dict, filepath):
    """
    dump le dict dans un fichier Json
    :param dict: dictionnary
    :param url: out filepath
    :return: write dict to jsonFile
    """
    print("to_json_file", filepath)

    with open(filepath, 'w') as file:
        file.write(json.dumps(dict, indent=4, separators=(',', ': ')))

def to_csv_file(data, filepath):
    """
    Enregistre une liste de dictionnaires dans un fichier CSV.
    :param data: Liste de dictionnaires à écrire dans le fichier CSV
    :param filepath: Chemin du fichier de sortie
    :return: None
    """

    print("to_csv_file", filepath)

    with open(filepath, mode='w+', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Écrire les en-têtes (noms des colonnes)
        try:
            headers = data[0].keys()
            writer.writerow(headers)
        except:
            print("[WARN] to_csv_file - data vide")

        # Écrire les données
        for row in data:
            writer.writerow(row.values())


def to_file(data, name, folder, extension="json"):

    filepath = os.path.join(folder, name+"."+extension)
        
    if extension == "json":
        to_json_file(data, filepath)
    elif extension == "csv":
        to_csv_file(data, filepath)
    else:
        print("[ERROR] FileType inconnu: ", extension)

def getFilename(libelle, extension="json"):
    # return date + libelle + .extension
    return datetime.datetime.now().strftime("%Y%m%d%H%M") + "_" + libelle + "." + extension

def add_0_before_int(number, length):
    page_str = str(number)
    while len(page_str) < length:
        page_str = "0" + page_str
    return page_str

def getPageSoup(url, use_delay = True):
    """
    return the soup from the page URL or tuple (url, err_html) if Error
    in case of 403 error wait DELAY_TIME seconds before retry, if second attempt fail: return error.
    :param url: page url
    :param use_delay: wait DELAY_PER_PAGE_SECONDS before request
    :return: beautifulSoup soup object ou tuple (url, error HTTP)
    """

    # 3 browsers complete header
    generic_headers = [
        {  # Header Chrome
            "accept": "*/*",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "referer": "https://search.brave.com/search?q=chrome+how+to+copy+http+header",
            "sec-ch-ua": "Not)A;Brand\";v =\"99\",\"Google Chrome\";v=\"127\",\"Chromium\";v=\"127",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        },
        {  # Header Chrome
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin"
        },
        {  # Header Edge
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "cookie": "TP.uuid=90ba2c24-79ec-407f-943b-f1cdbd5843ee",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
        }
    ]

    if use_delay:
        # DELAY FIXE + DELAY RANDOM (on ne wait pas pour la 1ere page)
        random_delay = random.random()
        time.sleep(DELAY_PER_PAGE_SECONDS + random_delay)

    page = None
    try:
        page = requests.get(url, headers=random.choice(generic_headers))
    except requests.exceptions.RequestException as Ex:
        # TODO: logguer les erreurs en base ou ailleurs
        print(str(Ex))

    # Analyse du retour
    if page != None:
        if page.status_code == 200:  # All is fine Return bs Soup
            return bs(page.content, "lxml")
        elif page.status_code != 403: # Erreur Html hors 403
            #print("[ERROR] getPageSoup - " + str(page) + " - " + url)
            return (url, page.status_code)
        else: # 403 We are spotted !
            # wait & retry meme si on n'utilise pas de delay
            # long delay
            print("getAllFirmReviewToJson - Error 403 - WAIT ", DELAY_TIME, "seconds START", url)
            time.sleep(DELAY_TIME)
            # Nouvelle tentative
            print("getAllFirmReviewToJson - RETRY")
            try:
                retry = requests.get(url, headers=random.choice(generic_headers))
            except requests.exceptions.RequestException as Ex:
                # TODO: logguer les erreurs en base ou ailleurs
                print(str(Ex))

            if retry.status_code == 200:
                return bs(page.content, "lxml")
            else:
                print("[ERROR] getPageSoup - Retry Failed:" + str(page) + " - " + url)
                return (url, page.status_code)
    else:
        print("[ERROR] getPageSoup - Request Failed:", url)

#todo: commentaires
def getLastPage(soup):

    paginationDiv = soup.find_all('nav', class_="pagination_pagination___F1qS") #bs 

    if paginationDiv is None:
        raise Exception("[ERROR] getAllCategorieFirmUrl: Page", soup[0], "doesn't have pagination")
    else:
        # Pagination presente, on ecrase la list
        paginationDiv = paginationDiv[0]
        # Je recupere d'abord le dernier lien de la pagination (last) et je recupere le lien precedent contenant le numero de la derniere page.

        bt_last = paginationDiv.find('a', attrs={"name": "pagination-button-last"})
        if bt_last is None:
            bt_next = paginationDiv.find('a', attrs={"name": "pagination-button-next"})  # bs
            if bt_next is None:
                return 1
            else:
                bt_last = bt_next.previous_sibling
        return int(bt_last.getText().replace("\u202f", ""))  # remplace l'espace separateur de millier (au cas ou)
        
def fileAggregation(folder_tmp, folder_out, file_name, json_output=True, csv_output=False):
    
    # recupere tous les fichiers du dossier
    files = [f for f in os.listdir(folder_tmp) if os.path.isfile(os.path.join(folder_tmp, f))]

    if len(files) == 0:
        raise Exception("fileAggregation - No files in "+ str(folder_tmp))

    files.sort()

    # creer fichier final
    final_file = []
    last_page = 0
    suivi_page = []
    reviews_count = 0
    file_count = len(files)
    err_sequence = []

    for page_url in files:
        file = open(os.path.join(folder_tmp, page_url),'r', encoding='utf-8')
        file_has_data = True

        try:
            data = json.load(file)
            tmp = data["data"]
        except:
            print("Le fichier n'a pas le format attendu, verifier les fichiers d'entrée, il y a un intru: "+page_url)
            file_has_data = False

        if file_has_data and tmp is not None: # evite le data["data"] absent et egal a None
            # Ajout a final list
            if data is not None:
                final_file += data["data"]

    # Écrire les données dans le fichier CSV
    if len(final_file) != 0:
        if csv_output:
            to_csv_file(final_file, os.path.join(folder_out,file_name+".csv"))

        if json_output:
            to_json_file(final_file, os.path.join(folder_out,file_name+".json"))
            print("json file generated")
    else:
        print("No new reviews")

