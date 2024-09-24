import datetime
import os.path
import datetime as dt
from datetime import timedelta

from src.firm_get_all_reviews import firm_get_onePage_reviews
from src.common import SITE_URI, TEMP_FOLDER, OUTPUT_FOLDER, getPageSoup, to_json_file, fileAggregation

#################################################"
# NOT FINISH YET
#################################################"

def getFirmList():
    f = open("conf//firms.properties", "r")
    return f.readlines()

def check_reviews(reviews, last_dt_extract, page):
    # Paranoia: je retrie le tableau de review
    sorted(reviews, key=lambda d: dt.datetime.strptime(d["review_date"],"%Y-%m-%d"), reverse=True)
    new_reviews = []
    more_review = True
    for rev in reviews:
        if dt.datetime.strptime(rev["review_date"],"%Y-%m-%d") > last_dt_extract:
            new_reviews.append(rev)
        else:
            more_review = False
            break
    # n conserve le meme format que les fichiers initialement crawlés pour utiliser les meme fonctions
    return ({"page": page, "data": new_reviews}, more_review)

def update_firms_reviews(last_dt_extract):
    today = dt.datetime.now().strftime("%Y%m%d")
    firm_list = getFirmList()
    for firm in firm_list:
        firm = firm.replace("\n","")
        page = 0
        more_review = True
        while more_review:
            page += 1
            # write uri
            filter = "?sort=recency"
            if page != 1:
                filter = "?page=" + str(page) + "&sort=recency"

            url = os.path.join(SITE_URI+"/review/", firm+filter)

            try: # connection
                reviews = firm_get_onePage_reviews(getPageSoup(url), url.split('?')[0])
            except Exception as e:
                raise e.message

            new_reviews, more_review = check_reviews(reviews, last_dt_extract, page)

            to_json_file(new_reviews, TEMP_FOLDER + today +"_"+ firm+".json")

    fileAggregation(TEMP_FOLDER, OUTPUT_FOLDER, today + "_updated_reviews", csv_output=True, json_output=True)

    print("stop")

# besoin de la derniere date d'extract

# UNIX
# DT_EXTRACT = os.getenv("dt_extract")

# Test Value
current_date = dt.date.today()
DT_EXTRACT = datetime.datetime.now() - timedelta(days=20)

update_firms_reviews(DT_EXTRACT)
