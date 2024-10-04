from bs4 import BeautifulSoup as bs
import requests
import json
import datetime
import time
import random
import csv
from os import listdir
from os.path import isfile, join



DELAY_PER_PAGE_SECONDS = 3

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

def getPageSoup(url):
    """
    return the soup from the page URL or tuple if Error
    create random http header simulating browsers
    :param url: page url
    :return: beautifulSoup soup object ou tuple (url, error HTTP) en ca d'erreur
    """
    print("getPageSoup(",url,")")
    # browser complete header
    generic_headers = [
        { # Header Chrome
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
        { # Header Chrome
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
        { # Header Edge
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

    page = None
    try:
        page = requests.get(url, headers=random.choice(generic_headers))
    except requests.exceptions.RequestException as Ex:
        # TODO: logguer les erreurs en base ou ailleurs
        print(str(Ex))

    if page != None:
        if page.status_code == 200: # All is fine !
            return bs(page.content, "lxml")
        elif page.status_code == 403: # We are spotted !
            print("[ERROR] getPageSoup - " + str(page) + " - " + url)
            return (url, page.status_code)
        else:
            print("[ERROR] getPageSoup - " + str(page) + " - " + url)
            return (url, page.status_code)

def firm_getFirmReviews(soup, page_url):
    """
    Get all Reviews from one Firm page, ALL BeautifulSoup Code
    :param soup: Bs soup of the page
    :param page_url: page url to retrieve trust-pilot id
    :return: list of dict:
        {
            "firm_url": firm_url str,
            "firm_name": firm_name str,
            "review_url": review_url str,
            "review_title": review_title str,
            "note": note int,
            "reponse": reponse bool ,
            "author_name": author_name str,
            "author_url": author_url str,
            "author_localisation": author_localisation str,
            "review_date": review_date date,
            "experience_date": experience_date date
        }
    """

    # on recupere l'id trustpilot de la firme dans l'url
    if "?page=" in page_url:
        firm_url = page_url.split("/")[-2]
    else:
        firm_url = page_url.split("/")[-1]

    firm_name = soup.find("span", "typography_display-s__qOjh6").getText().strip()

    review_card = soup.find_all('div', class_="styles_cardWrapper__LcCPA")
    reviews_all = []

    for rev in review_card:
        # Title
        review_title = rev.find("a", attrs={"data-review-title-typography": "true"}).getText()
        # NOTE
        img_src = rev.find("div", "star-rating_starRating__4rrcf").find("img")["src"]
        note = img_src.split("stars-")[1][:1]
        # URL
        review_url = rev.find("a", attrs={"data-review-title-typography": "true"})["href"]
        # REPONSE
        rep = rev.find("div", class_="paper_paper__1PY90")
        if rep is None:
            reponse = False
        else:
            reponse = True

        # NOM Auteur
        author_name = rev.find("span", attrs={"data-consumer-name-typography":"true"}).getText()
        author_url = rev.find("a", attrs={"name":"consumer-profile"})["href"]
        # le div pays n'est pas identifié donc je passe par sont icone

        author_localisation = rev.find("svg", class_="icon_icon__ECGRl")
        if author_localisation.nextSibling is not None:
            author_localisation = author_localisation.nextSibling.getText()
        else:
            author_localisation = None

        review_date = rev.find("time", attrs={"data-service-review-date-time-ago":"true"})["datetime"]
        experience_date = rev.find("p", attrs={"data-service-review-date-of-experience-typography":"true"}).getText().split(": ")[1]

        reviews_all.append({
            "firm_url": firm_url,
            "firm_name": firm_name,
            "review_url": review_url,
            "review_title": review_title,
            "note": note,
            "reponse": reponse,
            "author_name": author_name,
            "author_url": author_url,
            "author_localisation": author_localisation,
            "review_date": review_date,
            "experience_date": experience_date
        })
    return reviews_all

def getAllFirmReviewToJson(firm_url, output_folder):
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

    # recupere le nombre de page
    soup = getPageSoup(firm_url)

    if type(soup) is tuple: # erreur HTML != 200
        raise Exception("getAllFirmReviewToJson - Error on first connect, please check", soup[0], soup[1])
    else:
        # Recherche la pagination sur la page
        paginationDiv = soup.find_all('nav', class_="pagination_pagination___F1qS")
        if len(paginationDiv) == 0:
            raise Exception("[ERROR] exec_on_all_pages: Page",soup[0],"doesn't have pagination")
        else:
            # Pagination presente, on ecrase la list
            paginationDiv = paginationDiv[0]
            # Je recupere d'abord le dernier lien de la pagination (last) et je recupere le lien precedent contenant le numero de la derniere page.
            bt_next = paginationDiv.find('a', attrs={"name": "pagination-button-next"})
            bt_last = bt_next.previous_sibling
            last_page = int(bt_last.getText().replace("\u202f", ""))  # remplace l'espace separateur de millier (au cas ou)

            all_reviews = []
            url_in_error = []
            page_counter = 0

            for i in range(1, last_page + 1):
                # create URL
                if i == 1:  # url categorie sans ?page=i
                    url = firm_url
                else:
                    url = firm_url + "/?page=" + str(i)

                    if USE_DELAY:
                        # DELAY FIXE + DELAY RANDOM (on ne wait pas pour la 1ere page)
                        random_delay = random.random()
                        print("getAllFirmReviewToJson - delay ", DELAY_PER_PAGE_SECONDS, "+", random_delay, "seconds")
                        time.sleep(DELAY_PER_PAGE_SECONDS + random_delay)

                # Request TrustPilot
                page_soup = getPageSoup(url)

                # RETOUR HTML & WAIT
                # si on tombe sur une erreur 403:
                # on attend 2 minutes, on retente la page:
                #       si error: on place la page dans la liste d'erreur et on passe a la suivante
                #       sinon: la page continue dans le process normal
                if type(page_soup) is tuple: # erreur HTML
                    # Save in url_in_error
                    if page_soup[1] == 403: # WE ARE SPOTTED !! TAKE COVER
                        if USE_DELAY:
                            print("getAllFirmReviewToJson - Error 403 - WAIT ", 120, "seconds START"  )
                            time.sleep(120)
                            print("getAllFirmReviewToJson - Error 403 - WAIT END - ")
                            print("Retry "+ page_soup[0])
                            page_soup = getPageSoup(url)

                            if page_soup is tuple: # Page encore en erreur: on l'ajoute aux erreur pour traitement ulterieur et on passe a l'iteration suivante
                                print("Still in error: put in url_in_error and go to next page")
                                url_in_error.append(page_soup)
                                continue
                        else:
                            url_in_error.append(page_soup)
                            continue
                    else:
                        url_in_error.append(page_soup)
                        continue
                        print("getAllFirmReviewToJson - Error ", page_soup[1],"url:", page_soup[0])

                # PAGE OK: code HTML 200
                # execution function de crawl
                page_reviews = {"page": i, "reviews": firm_getFirmReviews(page_soup, url)}
                # ecriture json
                to_json_file(page_reviews,  output_folder + getJsonName(url, i))

            # Affichage des erreurs
            if len(url_in_error) > 0:
                print ("URL IN ERROR")
                for err in url_in_error:
                    print(str(err))
            else:
                print("NO ERROR")

    print("getAllFirmReviewToJson - START")

#################################################"
# MAIN
SITE_URI="https://www.trustpilot.com"
# Firms Reviews
TEST_FIRM_URI = SITE_URI + "/review/egcu.org"
#TEST_FIRM_REVIEW_OUTPUT_FILE = "C:\\tmp\\firm_EGCU_Reviews.json"

FIRM_URI = SITE_URI + "/review/turbodebt.com"
#FIRM_REVIEW_OUTPUT_FILE = "C:\\tmp\\firm_TurboDebt_Reviews.json"

OUTPUT_FOLDER = "C:\\tmp\\tmp2\\"

# GENERATION DES FICHIERS
getAllFirmReviewToJson(FIRM_URI, OUTPUT_FOLDER)



