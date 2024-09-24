import os.path
import shutil
from crawl.src.firm_get_all_reviews import *


#################################################"
# SCRIPT EXECUTABLE PAR BATCH

# INIT WORKING FOLDER
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

def get_firm_all_review(FIRM):
    FIRM_URI = SITE_URI + "/review/" + FIRM
    # CREATION DOSSIER
    print("Creation dossier Temp")
    folder_file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + "_" + FIRM + "_reviews"
    tmp_path = os.path.join(TEMP_FOLDER, folder_file_name)

    if os.path.exists(tmp_path): # suppr folder if exist
        shutil.rmtree(tmp_path)

    os.makedirs(tmp_path)
    print(tmp_path)

    # GENERATION DES FICHIERS DANS DOSSIER TEMP
    print("#######################################")
    print("Generation des fichiers Reviews")
    print("Firms",FIRM_URI)
    print("TEMP_FOLDER",TEMP_FOLDER)

    getAllFirmReviewToJson(FIRM_URI, tmp_path, extension="json", use_delay=USE_DELAY)

    print("#######################################")
    print("Aggregation")
    print("INPUT_FOLDER", tmp_path)
    print("OUTPUT_FOLDER", OUTPUT_FOLDER)
    print("file_name", folder_file_name)

    # Aggregation des fichiers
    fileAggregation(tmp_path, OUTPUT_FOLDER, folder_file_name, json_output=True, csv_output=True)

    # Verification
    # TODO

    # Effacement du dossier tmp
    print("#######################################")
    print("Suppresion du dossier tmp ", tmp_path)
    """
    try:
        shutil.rmtree(tmp_path)
    except Exception:
        print("ERROR while deleting tmp folder")
    """





USE_DELAY = True

# Mini cas 3 avis
# FIRM = "a1financialinc.com"

#FIRM = "www.ftrelief.us"
# Cas de test
#FIRM = "egcu.org"

# Cas reel
# FIRM = "turbodebt.com"

#FIRM = "freedomdebtrelief.com" # big One 1
#FIRM = "www.nationaldebtrelief.com" # big One 2
#FIRM = "www.creditassociates.com"
#FIRM = "americor.com"

#FIRM = "www.cafepress.com"

uri = ["cryptotask.net",
        "alphaboa.us", "scryptasicminer.com", "prostoobmen.com", "globaltraceassets.com",
        "cointrack.ai", "buycryptocurrencyatm.com", "vypr.ai", "aventure.vc",
        "dev.banpay.com", "castleconnect.io", "lifepreneur.com", "paybypago.com",
        "heliosfund.io", "givling.com", "allcoastfunding.com", "trustgeekshackexpert.com",
        "evolvedtrade.com", "dollarpe.com"
]

uri = open("C:\\Users\\steph\\OneDrive\\Documents\\Formation\\projets\\DATASET\\investments_wealth\\investments_wealth_all_firms_id.json").readlines()
start_dt=datetime.datetime.now()

wait = True
last_stop= "www.nationaldebtrelief.com"

for u in uri:
    if last_stop is not None:
        if last_stop in u:
            wait = False
            continue

    if not wait:
        u = u.replace("\n","")
        print("START-",u, start_dt)
        print("************************************")
        print(u)
        get_firm_all_review(u)
        print("END-", start_dt, datetime.datetime.now())
    else:
        print("wait - "+u)


