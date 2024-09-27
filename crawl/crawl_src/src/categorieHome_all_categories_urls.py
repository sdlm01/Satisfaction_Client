from firm_get_firm_infos import *
import re

def getCategoriesInfo(categorie_url):
    page_url = SITE_URI+categorie_url+"?sort=reviews_count"
    soup = getPageSoup(page_url)
    if type(soup) is tuple:
        if int(soup[1]) == 404:
            return (0,0)
        else:
            return soup
    else:
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

SITE_URI = "https://fr.trustpilot.com"
USE_DELAY = False

soup = getPageSoup(SITE_URI+"/categories", USE_DELAY)

all_cat_div = soup.find_all('div', class_="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_card__slNee")

all_cat_uri = []

for cat_div in all_cat_div:
    cat = cat_div.find('a', class_="link_internal__7XN06 link_wrapper__5ZJEx styles_headingLink__fl2dp")
    subcats = cat_div.find_all('li')

    try:
        cat["href"]
    except:
        print("stop")

    sub_link = []
    for s in subcats:
        link = s.find('a')
        sub_link.append({
            "subcat":link.getText(),
            "subcat_uri":link["href"],
        })
    
    all_cat_uri.append({
        "cat": cat.getText(),
        "cat_uri": cat["href"],
        "sub_cat":sub_link
    })

final = []
for cat in all_cat_uri:
    print("####################")
    info_cat = getCategoriesInfo(cat["cat_uri"])
    print(cat["cat"], info_cat)
    sub_list = []
    for sub in cat["sub_cat"]:

        info = getCategoriesInfo(sub["subcat_uri"])
        print("\t", sub["subcat"], info)
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

to_json_file(final,os.path.join(OUTPUT_FOLDER,"stat_categ.json"))
print("stop")
    

