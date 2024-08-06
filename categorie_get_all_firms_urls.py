from bs4 import BeautifulSoup as bs

import datetime
import time
import random
import csv
from os import listdir
from os.path import isfile, join

from common import getPageSoup, getLastPage

from firm_get_firm_infos import *

def categorie_get_onePage_firms_urls(soup):
    """
    categorie_get_onePage_firms_urls
    :param soup: soup de la page categorie
    :return: liste des url presentes sur la page en param
    """
    firms_urls = soup.find_all('a', attrs={"name": "business-unit-card"})
    urls = []
    for url in firms_urls:
        urls.append(url["href"])
    return urls


def categorie_get_all_firms_urls(categorie_url):
    """
    Retourne toutes les reviews d'une firme
    :param categorie_url: url de la page de la categorie
    :param filepath_out: str chemin du fichier de sortie
    :return: void
    """

    # #########################
    # ATTENTION: VARIABLE DE DEV USE_DELAY
    # j'utilise cette variable pour faire sauter la gestion de l'erreur 403 et le delay de 3 secondes.
    # ca permet d'eviter que le test sur un petit jeu de données attende 3s entre chaques appels.
    # TODO plus tard: Regler le delais en fonction du nombre de page a recuperer

    USE_DELAY = False

    print("categorie_get_all_firms_urls - START")
    # recupere le nombre de page
    soup = getPageSoup(categorie_url)

    if type(soup) is tuple:  # erreur HTML != 200
        raise Exception("[ERROR] categorie_get_all_firms_urls - Error on first connect, please check", soup[0], soup[1])
    else:
        # Recherche la derniere page, Exception si pagination absente
        last_page = getLastPage(soup)

        url_in_error = []
        firms_urls = []

        for i in range(1, last_page + 1):
            # create URL
            if i == 1:  # url categorie sans ?page=i
                url = categorie_url
            else:
                url = categorie_url + "/?page=" + str(i)

                if USE_DELAY:
                    # DELAY FIXE + DELAY RANDOM (on ne wait pas pour la 1ere page)
                    random_delay = random.random()
                    print("categorie_get_all_firms_urls - delay ", DELAY_PER_PAGE_SECONDS, "+", random_delay, "seconds")
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
                        print("categorie_get_all_firms_urls - Error 403 - WAIT ", 120, "seconds START")
                        time.sleep(120)
                        print("categorie_get_all_firms_urls - Error 403 - WAIT END - ")
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
                    print("categorie_get_all_firms_urls - Error ", page_soup[1], "url:", page_soup[0])

            # PAGE OK: code HTML 200
            # execution function de crawl
            firms_urls += categorie_get_onePage_firms_urls(page_soup)

        # Affichage des erreurs
        if len(url_in_error) > 0:
            print("URL IN ERROR")
            for err in url_in_error:
                print(str(err))
        else:
            print("NO ERROR")

        return firms_urls

    print("categorie_get_all_firms_urls - END")