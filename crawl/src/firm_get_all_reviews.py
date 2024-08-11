from crawl.src.common import *
import datetime

def firm_get_onePage_reviews(soup, page_url):
    """
    Get all Reviews from one Firm review page, ALL BeautifulSoup Code
    url example: https://www.trustpilot.com/review/turbodebt.com
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

        # for cross plateform
        tmp_split = experience_date.split(" ")

        exp_datetime = datetime.datetime.strptime(tmp_split[0]+tmp_split[1][:-1]+tmp_split[2], "%B%d%Y")

        # Text complet
        review_text = soup.find("p", "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn").getText()

        reviews_all.append({
            "firm_url": firm_url,
            "firm_name": firm_name,
            "review_url": review_url,
            "review_title": review_title,
            "review_text": review_text,
            "note": note,
            "reponse": reponse,
            "author_name": author_name,
            "author_url": author_url,
            "author_localisation": author_localisation,
            "review_date": review_date,
            "experience_date": exp_datetime.isoformat(),
            "extract_date": datetime.datetime.now().isoformat()
        })
    return reviews_all

def getAllFirmReviewToJson(firm_url, output_folder, extension="json", use_delay=True):
    """
    Crée un fichier json pour chaque page de reviews d'une firme
    format du Json: voir firm_getFirmReviews
    :param firm_url: url de la page de la firme
    :param filepath_out: str chemin du dossier de sortie
    :return: void
    """
    USE_DELAY = use_delay

    print("getAllFirmReviewToJson - START")

    # TEST ERREURs: ON SKIPPE lae for

    # recupere le nombre de page
    soup = getPageSoup(firm_url, use_delay=False) # Sans delay car 1ere connection

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

            # Request TrustPilot
            page_soup = getPageSoup(url, use_delay=USE_DELAY)

            if type(page_soup) is tuple: # erreur HTML
                url_in_error.append(page_soup)
                continue
            else:
                page_reviews = {"page": i, "data": firm_get_onePage_reviews(page_soup, url)}
                # fileName
                firm_id = firm_url.split("/")[-1]
                page_number = i
                filename = "firm_reviews" + "_" + firm_id + "_" + add_0_before_int(page_number, 4)
                # ecriture json
                to_file(page_reviews,  filename, folder=output_folder, extension=extension)

    # Traitement des erreurs
    if len(url_in_error) == 0:
        print("NO ERROR")
    else:
        print ("RETRY URL IN ERROR")
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
                print ("STILL IN ERROR: Manual check needed")
                still_in_error.append(err)
            else:
                page_reviews = {"page": page_number, "data": firm_get_onePage_reviews(soup, err[0])}
                filename = "firm_reviews" + "_" + firm_id + "_" + add_0_before_int(page_number, 4)
                # ecriture json
                to_file(page_reviews,  filename, folder=output_folder, extension=extension)
                print ("CORRECTED")
                
        print("RECAP RETRY")
        if len(still_in_error)==0: print("Aucune erreur restante")
        else:
            for x in still_in_error: 
                print("Reprise manuelle nescessaire")
                print(x)
