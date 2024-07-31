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
        headers = data[0].keys()
        writer.writerow(headers)
        # Écrire les données
        for row in data:
            writer.writerow(row.values())


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
            page_str = "0" + page_str

    return today.strftime("%Y%m%d-%H-%M") + "_categorieFirms" + "_" + firm_id + "_" + str(page_str) + ".json"


def getPageSoup(url):
    """
    return the soup from the page URL or tuple if Error
    create random http header simulating browsers
    :param url: page url
    :return: beautifulSoup soup object ou tuple (url, error HTTP) en ca d'erreur
    """
    print("getPageSoup(", url, ")")
    # browser complete header
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

    page = None
    try:
        page = requests.get(url, headers=random.choice(generic_headers))
    except requests.exceptions.RequestException as Ex:
        # TODO: logguer les erreurs en base ou ailleurs
        print(str(Ex))

    if page != None:
        if page.status_code == 200:  # All is fine !
            return bs(page.content, "lxml")
        elif page.status_code == 403:  # We are spotted !
            print("[ERROR] getPageSoup - " + str(page) + " - " + url)
            return (url, page.status_code)
        else:
            print("[ERROR] getPageSoup - " + str(page) + " - " + url)
            return (url, page.status_code)


def firm_getFirmInfo(url):
    """
    firm_getFirmInfo
    :param url: url de la page firm
    :return:
        {
        "page_url" str: page crawlée,
        "firm_id" str: id trust-pilot,
        "firm_url" str: url site firm,
        "name" str: firm name,
        "note" float: note,
        "verified" bool: bool verified,
        "nb_review" int: int review count,
        "firm_star_percs" dict: dict of percent/stars:
        "domain" str: firm domain,
        "extract_date" str: date of extract
        }
    """
    soup = getPageSoup(url)

    if type(soup) is tuple:  # erreur HTML != 200
        print("[ERROR] firm_getFirmInfo - Error on first connect, please check", soup[0], soup[1])
        return False
    else:
        # page url: url de la page crawlée
        page_url = url
        # tp_url: url servant d'id sur trust-pilot
        if "?page=" in page_url:
            firm_id = page_url.split("/")[-2]
        else:
            firm_id = page_url.split("/")[-1]

        name = soup.find("span", "typography_display-s__qOjh6").getText().strip()
        note = float(soup.find("p", "typography_body-l__KUYFJ").getText())
        # bool verified
        if soup.find("div", "typography_body-xs__FxlLP") is None:
            verified = False
        else:
            verified = True

        review_raw = soup.find('p', class_="typography_body-l__KUYFJ", attrs={"data-reviews-count-typography": "true"})
        # supprimer les separateurs de milliers possibles
        review_raw = review_raw.getText().replace(",", "").replace(" ", "")
        # ne garde que le numeric, remplacer par regexp
        try:
            # todo: remplacer par regexp
            nb_review = ""
            for i in review_raw:
                if not i.isnumeric():
                    break
                else:
                    nb_review += i
            nb_review = int(nb_review)
        except ValueError:
            print("firm_getFirmInfo - ValueError: " + str(ValueError))

        # Verification de l'ordre des pourcentages, on recupere les labels et on teste le premier
        stars = soup.find_all('p', class_="typography_body-m__xgxZ_",
                              attrs={"data-rating-label-typography": "true"})
        percs = soup.find_all('p', class_="typography_body-m__xgxZ_",
                              attrs={"data-rating-distribution-row-percentage-typography": "true"})

        # firm_star_percs est un Dict pour garantir l'ordre des etoiles
        firm_star_percs = {}
        for i in range(0, len(percs)):
            firm_star_percs[stars[i].getText().replace("-star", "")] = percs[i].getText().replace("%", "")

        # Domain
        domain_p = soup.find("p", "typography_body-m__xgxZ_")
        domain = domain_p.find('a').getText()
        breadCrumb = soup.find("ol", class_="breadcrumb_breadcrumbList__Wa1xu")
        subcat_raw = breadCrumb.find_all("a")
        subcat_list = []
        for subcat in subcat_raw:
            subcat_list.append(subcat.getText())
        # On supprimer la derniere subcat: c'est le nom de l'entreprise
        subcat_list.pop(-1)

        contact = soup.find("div", "card_cardContent__sFUOe")

        telephone = ""
        mail = ""
        localisation = ""
        contact1 = []
        for element in soup.find_all("a",
                                     class_="link_internal__7XN06 typography_body-m__xgxZ_ typography_appearance-action__9NNRY link_link__IZzHN link_underlined__OXYVM"):
            contact1.append(element.get_text())
            if len(contact1) == 2:
                mail = contact1[0]
                telephone = contact1[1]
            elif len(contact1) == 1 and "@" in contact1[0]:
                telephone = ""
                mail = contact1[0]
            elif len(contact1) == 1:
                telephone = contact1[0]
                mail = ""

        localisation = []
        for element in soup.find_all("ul",
                                     class_="typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_contactInfoAddressList__RxiJI"):
            for element2 in element.find_all("li"):
                localisation.append(element2.get_text())

        return {
            "page_url": page_url,
            "firm_id": firm_id,
            "name": name,
            "note": note,
            "verified": verified,
            "nb_review": nb_review,
            "firm_star_percs": firm_star_percs,
            "domain": domain,
            "subcat": subcat_list,
            "extract_date": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "telepone": telephone,
            "mail": mail,
            "localisation": localisation
        }


def categorie_getFirmsUrls(soup):
    """
    categorie_getFirmsUrls
    :param soup: soup de la page categorie
    :return: liste des url presentes sur la page en param
    """
    firms_urls = soup.find_all('a', attrs={"name": "business-unit-card"})
    urls = []
    for url in firms_urls:
        urls.append(url["href"])
    return urls


def getAllCategorieFirmUrl(firm_url, output_folder):
    """
    Retourne toutes les reviews d'une firme
    :param firm_url: url de la page de la firme
    :param filepath_out: str chemin du fichier de sortie
    :return: void
    """

    # #########################
    # ATTENTION: VARIABLE DE DEV USE_DELAY
    # j'utilise cette variable pour faire sauter la gestion de l'erreur 403 et le delay de 3 secondes.
    # ca permet d'eviter que le test sur un petit jeu de données attende 3s entre chaques appels.
    # TODO plus tard: Regler le delais en fonction du nombre de page a recuperer

    USE_DELAY = False

    print("getAllCategorieFirmUrl - START")
    # recupere le nombre de page
    soup = getPageSoup(firm_url)

    if type(soup) is tuple:  # erreur HTML != 200
        raise Exception("[ERROR] getAllCategorieFirmUrl - Error on first connect, please check", soup[0], soup[1])
    else:
        # Recherche la pagination sur la page
        paginationDiv = soup.find_all('nav', class_="pagination_pagination___F1qS")
        if len(paginationDiv) > 1:
            raise Exception("[ERROR] getAllCategorieFirmUrl: Page", soup[0], "doesn't have pagination")
        else:
            # Pagination presente, on ecrase la list
            paginationDiv = paginationDiv[0]
            # Je recupere d'abord le dernier lien de la pagination (last) et je recupere le lien precedent contenant le numero de la derniere page.
            bt_next = paginationDiv.find('a', attrs={"name": "pagination-button-next"})
            bt_last = bt_next.previous_sibling
            last_page = int(
                bt_last.getText().replace("\u202f", ""))  # remplace l'espace separateur de millier (au cas ou)

            all_reviews = []
            url_in_error = []
            page_counter = 0
            firms_urls = []

            for i in range(1, last_page + 1):
                # create URL
                if i == 1:  # url categorie sans ?page=i
                    url = firm_url
                else:
                    url = firm_url + "/?page=" + str(i)

                    if USE_DELAY:
                        # DELAY FIXE + DELAY RANDOM (on ne wait pas pour la 1ere page)
                        random_delay = random.random()
                        print("getAllCategorieFirmUrl - delay ", DELAY_PER_PAGE_SECONDS, "+", random_delay, "seconds")
                        time.sleep(DELAY_PER_PAGE_SECONDS + random_delay)

                # Request TrustPilot
                page_soup = getPageSoup(url)

                # RETOUR HTML & WAIT
                # si on tombe sur une erreur 403:
                # on attend 2 minutes, on retente la page:
                #       si error: on place la page dans la liste d'erreur et on passe a la suivante
                #       sinon: la page continue dans le process normal
                if type(page_soup) is tuple:  # erreur HTML
                    # Save in url_in_error
                    if page_soup[1] == 403:  # WE ARE SPOTTED !! TAKE COVER
                        if USE_DELAY:
                            print("getAllCategorieFirmUrl - Error 403 - WAIT ", 120, "seconds START")
                            time.sleep(120)
                            print("getAllCategorieFirmUrl - Error 403 - WAIT END - ")
                            print("Retry " + page_soup[0])
                            page_soup = getPageSoup(url)

                            if page_soup is tuple:  # Page encore en erreur: on l'ajoute aux erreur pour traitement ulterieur et on passe a l'iteration suivante
                                print("Still in error: put in url_in_error and go to next page")
                                url_in_error.append(page_soup)
                                continue
                        else:
                            url_in_error.append(page_soup)
                            continue
                    else:
                        print("getAllCategorieFirmUrl - Error ", page_soup[1], "url:", page_soup[0])

                # PAGE OK: code HTML 200
                # execution function de crawl
                firms_urls += categorie_getFirmsUrls(page_soup)

            # Affichage des erreurs
            if len(url_in_error) > 0:
                print("URL IN ERROR")
                for err in url_in_error:
                    print(str(err))
            else:
                print("NO ERROR")

            return firms_urls

    print("getAllCategorieFirmUrl - END")


#################################################"
# MAIN
SITE_URI = "https://www.trustpilot.com"
CATEGORIE_URI = SITE_URI + "/categories/atm"
CATEGORIE = CATEGORIE_URI.split("/")[-1]

OUTPUT_FOLDER = "C:\\tmp\\categorie_firm\\"

print("Recherche des urls des entreprises pour la categorie: ", CATEGORIE)
firms_uri = getAllCategorieFirmUrl(CATEGORIE_URI, OUTPUT_FOLDER)
print(len(firms_uri), "firmes trouvées")

# recup firm info
print("parcours des urls")
uri_in_error = []
all_firm_info = []
for uri in firms_uri:
    uri = SITE_URI + uri
    data = firm_getFirmInfo(uri)
    if data == False:
        uri_in_error.append(uri)
    else:
        all_firm_info.append(data)
print(len(all_firm_info), "firms crawlées")

filename = datetime.datetime.today().strftime("%Y%m%d-%H-%M") + "_categorieFirmsInfo" + "_" + CATEGORIE + ".json"

print("ecriture du json", OUTPUT_FOLDER + filename)

JSON_OUTPUT= True
CSV_OUTPUT= False

if JSON_OUTPUT:
    print("write final file")
    to_json_file(all_firm_info, join(OUTPUT_FOLDER, f"all_reviews_{CATEGORIE}.json"))

if CSV_OUTPUT:
    print("write final CSV file")
    to_csv_file(all_firm_info, join(OUTPUT_FOLDER, f"all_reviews_{CATEGORIE}.csv"))

to_json_file(all_firm_info, OUTPUT_FOLDER + filename)



