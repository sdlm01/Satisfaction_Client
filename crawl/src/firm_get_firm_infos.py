import re
from common import *
from categorie_get_all_firms_urls import *

USE_DELAY = False

def firm_getFirmInfo(url):


    if type(url) is str: # si url seule on la met ds une list
        url = [url]

    url_in_error = []
    all_firm_info = []
    for uri in url:
        print(uri)
        uri = SITE_URI + uri
        soup = getPageSoup(uri, use_delay=USE_DELAY)
        if type(soup) is tuple:  # si url seule on la met ds une list
            print("[ERROR]",tuple)
            url_in_error.append(soup)
        else:
            all_firm_info.append(firm_get_oneFirm_infos(soup, uri))

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
                all_firm_info.append(firm_get_oneFirm_infos(soup, uri))

        print("RECAP RETRY")
        if len(still_in_error) == 0:
            print("Aucune erreur restante")
        else:
            for x in still_in_error:
                print("Reprise manuelle nescessaire")
                print(x)


    return all_firm_info


def firm_get_oneFirm_infos(soup, page_url): #soup, page_url
    """
    firm_getFirmInfo
    :param url: url de la page Entreprise
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
        nb_review = int(re.sub("[^0-9]", "", review_raw))
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
        firm_star_percs[int(stars[i].getText().replace("-star", ""))] = int(re.sub("[^0-9]", "", percs[i].getText()))

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
        "telepone": telephone,
        "mail": mail,
        "localisation": localisation,
        "extract_date": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    }