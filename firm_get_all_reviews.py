from bs4 import BeautifulSoup as bs
import json
import datetime
import time
import random
import csv
import os

from common import *

def firm_get_onePage_reviews(soup, page_url):
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
            "experience_date": experience_date,
            "extract_date": datetime.datetime.now().isoformat()
        })
    return reviews_all

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

    # recupere le nombre de page
    soup = getPageSoup(firm_url)

    if type(soup) is tuple: # erreur HTML != 200
        raise Exception("getAllFirmReviewToJson - Error on first connect, please check", soup[0], soup[1])
    else:
        # Recherche la derniere page, Exception si pagination absente
        last_page = getLastPage(soup)

        url_in_error = []

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
            page_reviews = {"page": i, "data": firm_get_onePage_reviews(page_soup, url)}

            # FileName
            if "?page=" in url:
                firm_id = url.split("/")[-2]
                page_number = url.split("=")[-1]
            else:
                firm_id = url.split("/")[-1]
                page_number = 1

            today = datetime.datetime.now()

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

# Cas de test
FIRM = "egcu.org"

# Cas reel
#FIRM = "turbodebt.com"

FIRM_URI = SITE_URI +"/review/"+ FIRM

# CREATION DOSSIER
folder_file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + "_" + FIRM + "_reviews"
tmp_path = os.path.join(TEMP_FOLDER, folder_file_name)
os.mkdir(tmp_path)

# GENERATION DES FICHIERS DANS DOSSIER TEMP

print("Generation des fichiers Reviews")
print("Firms",FIRM_URI)
print("TEMP_FOLDER",TEMP_FOLDER)
print("Generation des fichiers Reviews")

getAllFirmReviewToJson(FIRM_URI, tmp_path, extension="json")
# Aggregation des fichiers
fileAggregation(tmp_path, OUTPUT_FOLDER, folder_file_name, json_output=True, csv_output=True)
# Verification
# TODO

# Effacement du dossier temp
os.remove(tmp_path)


