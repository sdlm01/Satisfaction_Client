from .firm_get_firm_infos import *
from .common import *

def categorie_get_onePage_firms_urls(soup):
    """
    categorie_get_onePage_firms_urls
    :param soup: soup de la page categorie
    :return: liste des url firm presentes sur la page
    """
    firms_urls = soup.find_all('a', attrs={"name": "business-unit-card"})
    urls = []
    for url in firms_urls:
        urls.append(url["href"])
    return urls


def categorie_get_all_firms_urls(categorie_url, use_delay=False):
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
    USE_DELAY = use_delay

    print("categorie_get_all_firms_urls - START")
    # recupere le nombre de page
    soup = getPageSoup(categorie_url, use_delay=False) # 1ere connection pas de delay

    if type(soup) is tuple:  # erreur HTML on interromp le process
        raise Exception("[ERROR] categorie_get_all_firms_urls - Error on first pers_connect.py, please check", soup[0], soup[1])

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

        # Request TrustPilot
        page_soup = getPageSoup(url, use_delay=USE_DELAY)
        if type(page_soup) is tuple:
            url_in_error.append(page_soup)
            continue
        else:
            firms_urls += categorie_get_onePage_firms_urls(page_soup)
            print("url added:",len(firms_urls))

    # Traitement des erreurs
    if len(url_in_error) == 0:
        print("NO ERROR")
    else:
        print("RETRY URL IN ERROR")
        still_in_error = []
        for err in url_in_error:
            print(str(err))

            # Decoupage url in error to get firm_id + page_number
            if "?page=" in err[0]:
                tmp_split = err[0].split("?page=")
                firm_id = tmp_split[0].split("/")[-1]
                page_number = int(tmp_split[-1])
            else:
                firm_id = err[0].split("/")[-1]
                page_number = 1

            # on utilise le delay pour le retry des erreurs
            soup = getPageSoup(err[0], use_delay=True)

            if type(soup) is tuple:
                print("STILL IN ERROR: Manual check needed")
                still_in_error.append(err)
            else:
                firms_urls += categorie_get_onePage_firms_urls(page_soup)
                print("CORRECTED")

        print("RECAP RETRY")
        if len(still_in_error) == 0:
            print("Aucune erreur restante")
        else:
            for x in still_in_error:
                print("Reprise manuelle nescessaire")
                print(x)

    return firms_urls

    print("categorie_get_all_firms_urls - END")