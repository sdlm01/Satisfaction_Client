import os.path
import json
from Param import Param
from Database import Database

import src.firm_get_all_reviews as crawl_review
import src.firm_get_firm_infos as crawl_firmInfo
import src.common as common
from datetime import date
from datetime import datetime

#################################################
# SCRIPT EXECUTABLE PAR BATCH
#################################################

def check_reviews(reviews, last_dt_extract, page):
    # Paranoia: je retrie le tableau de review
    
    sorted(reviews, key=lambda d: datetime.strptime(d["review_date"],"%Y-%m-%d"), reverse=True)
    new_reviews = []
    more_review = True

    ext_date = last_dt_extract
    if isinstance(last_dt_extract, str):
        ext_date = datetime.strptime(firm['extract_date'], '%Y-%m-%d')


    for rev in reviews:
        if datetime.strptime(rev["review_date"],"%Y-%m-%d") > ext_date:
            new_reviews.append(rev)
        else:
            more_review = False
            break
    # n conserve le meme format que les fichiers initialement crawlés pour utiliser les meme fonctions
    return ({"page": page, "data": new_reviews}, more_review)

def update_firm_reviews(firm, last_dt_extract):
    page = 0
    more_review = True
    firm_new_review = []

    while more_review:
        page += 1
        # write uri
        filter = "?sort=recency"
        if page != 1:
            filter = "?page=" + str(page) + "&sort=recency"

        url = os.path.join(SITE_URI+"/review/", firm+filter)

        try: # connection
            reviews = crawl_review.firm_get_onePage_reviews(common.getPageSoup(url), url.split('?')[0])
        except Exception as e:
            raise e.message

        if reviews != None:
            new_reviews, more_review = check_reviews(reviews, last_dt_extract, page)
            # print review nb
            print("page: {} - new review: {}".format(new_reviews["page"], len(new_reviews["data"])))
            
            firm_new_review.append(new_reviews["data"])
        else:
            more_review = False

    total_rev = 0
    for page in firm_new_review:
        if len(page) != 0:
            total_rev += len(page)
            db.insert_review(page, last_dt_extract, new_extract_date)
    
    return total_rev

def update_firm_infos(firm, new_extract_date):

    soup = common.getPageSoup(firm['page_url'], firm['firm_id'])
    data = crawl_firmInfo.firm_get_oneFirm_infos(soup, firm['page_url'])

    actual_firmInfo = db.normalize_firm_data(data, new_extract_date)


    fields_to_check = ['firm_name','localisation','mail','nb_review','note','subcat','domain','verified']
    update = False
    for key in fields_to_check:
        if actual_firmInfo[key] != firm[key]:
            update = True
            break

    if update:
        print("firmInfo updated")
        db.insert_firmInfos(actual_firmInfo, new_extract_date)
    else: 
        print("firmInfo not updated: No change")
    
    
    
    




# #############################################
# EXECUTION
# #############################################

# MONGO QUERY
# { extract_date: { "$lt": ISODate("2024-10-01T00:00:00Z") } }

# TODO: recuperer le PARAM_FOLDER DANS LA VAR d'ENV
PARAM_FOLDER = "/app/conf/"
PARAM_FILE_JSON = "conf.json"

param = Param(PARAM_FOLDER, PARAM_FILE_JSON)

SITE_URI = param.SITE_URI
OUTPUT_FOLDER = param.OUTPUT_FOLDER

new_extract_date = date.today()

db = Database(
    param.MONGO_DB_HOST,
    param.MONGO_DB_PORT,
    param.MONGO_DB_USERNAME,
    param.MONGO_DB_PASSWORD
)

# Initialisation de la base de données
if db.get_db() is None:
    raise Exception("exe_update_review.py - MongoDb non initialisé")

firm_list = db.get_firms_list()

print("Update Entreprises - START ", datetime.now())
total_rev = 0
for firm in firm_list:
    print("--------------------------------")
    print("update", firm['firm_id'])

    updated_rev = 0

    try:
        updated_rev = update_firm_reviews(firm['firm_id'], firm['extract_date'])
    except Exception as e:      
        raise(e)
    
    update_firm_infos(firm, new_extract_date)
    
    total_rev += updated_rev 

print("Total Updated Reviews", total_rev)

print("Update Entreprises - END ", datetime.now())

    


    




