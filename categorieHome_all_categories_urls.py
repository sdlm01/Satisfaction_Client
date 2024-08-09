from bs4 import BeautifulSoup as bs

import datetime
import time
import random
import csv
from os import listdir
from os.path import isfile, join
import re
from common import *
from categorie_get_all_firms_urls import *
from firm_get_firm_infos import *

def getCategoriesInfo(categorie_url):
    page_url = SITE_URI+categorie_url+"?sort=reviews_count"
    soup = getPageSoup(page_url)

    reviews_count=0
    reviews = soup.find_all('p', class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_ratingText__yQ5S7")
    for rev in reviews:
        # supprimer les separateurs de milliers possibles
        rev_count = rev.getText().replace(",", "").replace(" ", "").split("|")[1]
        rev_count = int(re.sub("[^0-9]", "", rev_count))
        reviews_count += rev_count
        
    last_page = getLastPage(soup)

    return (reviews_count, last_page)

#################################################"
# MAIN

SITE_URI = "https://www.trustpilot.com"
USE_DELAY = False

soup = getPageSoup(SITE_URI+"/categories", USE_DELAY)

all_cat_div = soup.find_all('div', class_="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_card__slNee")

all_cat_uri = []

for cat_div in all_cat_div:
    master = soup.find('a', class_="link_internal__7XN06 link_wrapper__5ZJEx styles_headingLink__fl2dp")
    subcats = soup.find_all('a', class_="link_internal__7XN06 typography_body-m__xgxZ_ typography_appearance-default__AAY17 typography_color-inherit__TlgPO link_link__IZzHN link_notUnderlined__szqki")
    sub_link = []
    for s in subcats:
        sub_link.append({
            "subcat":s.getText(),
            "subcat_uri":s["href"],
        })
    
    all_cat_uri.append({
        "cat": master.getText(),
        "cat_uri": master["href"],
        "sub_cat":sub_link
    })

final = []
for cat in all_cat_uri:
    print("####################")
    print(cat["cat"])
    info_cat = getCategoriesInfo(cat["cat_uri"])
    sub_list = []
    for sub in cat["sub_cat"]:
        print(sub["subcat"])
        info = getCategoriesInfo(sub["subcat_uri"])
        sub_list.append({
                "subcat": sub["subcat"],
                "subcat_uri": sub["subcat_uri"],
                "subcat_first_reviews":info[0],
                "subcat_last_page":info[1]
            })
        
    final.append({
        "cat": cat["cat"],
        "cat_uri": cat["cat_uri"],
        "cat_first_reviews":info_cat[0],
        "cat_last_parge":info_cat[1]
    })
    
print("stop")
    

