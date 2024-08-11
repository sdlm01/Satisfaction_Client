import datetime
from bs4 import BeautifulSoup as bs
import random
import csv
import requests
import json
import time
import os



SITE_URI = "https://www.trustpilot.com"

#OUTPUT_FOLDER = "/home/ubuntu/WORK/Scrap/out"
#TEMP_FOLDER = "/home/ubuntu/WORK/Scrap/tmp"

OUTPUT_FOLDER = "C:\\tmp\\out\\"
TEMP_FOLDER = "C:\\tmp\\"


DELAY_PER_PAGE_SECONDS = 3
DELAY_TIME = 120

JSON_OUTPUT= True
CSV_OUTPUT= False

def to_json_file(dict, filepath):
    """
    dump le dict dans un fichier Json
    :param dict: dictionnary
    :param url: output filepath
    :return: write dict to jsonFile
    """
    with open(filepath, 'w') as file:
        file.write(json.dumps(dict, indent=4, separators=(',', ': ')))

def to_csv_file(data, filepath):
    """
    Enregistre une liste de dictionnaires dans un fichier CSV.
    :param data: Liste de dictionnaires à écrire dans le fichier CSV
    :param filepath: Chemin du fichier de sortie
    :return: None
    """
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Écrire les en-têtes (noms des colonnes)
        try:
            headers = data["data"][0].keys()
            writer.writerow(headers)
        except:
            print("[WARN] to_csv_file - data vide")

        # Écrire les données
        for row in data["data"]:
            writer.writerow(row.values())


def to_file(data, name, folder=TEMP_FOLDER, extension="json"):
    print("to_file:",folder,"/"+name+"."+extension)

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

def getPageSoup(url, use_delay = False):
    """
    return the soup from the page URL or tuple (url, err_html) if Error
    in case of 403 error wait DELAY_TIME seconds before retry, if second attempt fail: return error.
    :param url: page url
    :param use_delay: wait DELAY_PER_PAGE_SECONDS before request
    :return: beautifulSoup soup object ou tuple (url, error HTTP)
    """
    #print("getPageSoup(", url, ")")

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
            print("getAllFirmReviewToJson - Error 403 - WAIT ", DELAY_TIME, "seconds START")
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
                print("[ERROR] getPageSoup - " + str(page) + " - " + url)
                return (url, page.status_code)

#todo: commentaires
def getLastPage(soup):

    paginationDiv = soup.find_all('nav', class_="pagination_pagination___F1qS") #bs 
    
    if len(paginationDiv) > 1:
        raise Exception("[ERROR] getAllCategorieFirmUrl: Page", soup[0], "doesn't have pagination")
    else:
        # Pagination presente, on ecrase la list
        paginationDiv = paginationDiv[0]
        # Je recupere d'abord le dernier lien de la pagination (last) et je recupere le lien precedent contenant le numero de la derniere page.
        bt_next = paginationDiv.find('a', attrs={"name": "pagination-button-next"}) #bs 
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

    csv_header = []
    first_page = True
    for page_url in files:
        file = open(os.path.join(folder_tmp, page_url),'r', encoding='utf-8')
        

        try:
            data = json.load(file)
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
        reviews_count += len(data["data"])

        # Ajout a final list
        final_file += data["data"]

        if len(final_file) == 0:
            print("empty data on file")

    # Écrire les données dans le fichier CSV
    if csv_output:
        to_csv_file(data, os.path.join(folder_out,file_name+".csv"))
        """ TODO TESTER AVANT DE SUPPR
        file_path = os.path.join(folder_out,file_name+".csv")

        csv_file = open(file_path, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        # csv_header = ["firm_url", "firm_name", "review_url", "review_title", "note", "reponse", "author_name", "author_url", "author_localisation", "review_date", "experience_date"]
        csv_writer.writerow(csv_header)

        for review in data["data"]:
            row_list = []
            for col in csv_header:
                row_list.append(review[col])
            
            csv_writer.writerow(row_list)

            print("page", data["page"], "saved in memory")

        # Fermeture du fichier CSV
        csv_file.close()
        print("csv file generated")
        """

    if json_output:
        to_json_file(final_file, os.path.join(folder_out,file_name+".json"))
        print("json file generated")
    
    print("Bilan aggregation")
    print("file count", file_count)
    print("reviews count", reviews_count)

