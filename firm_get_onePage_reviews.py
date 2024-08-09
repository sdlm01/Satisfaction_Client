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