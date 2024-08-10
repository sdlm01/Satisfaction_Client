import shutil
from firm_get_all_reviews import *

#################################################"
# SCRIPT EXECUTABLE PAR BATCH

# INIT WORKING FOLDER
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

USE_DELAY = True

# Mini cas 3 avis
FIRM = "priveeshop.com"
# Cas de test
#FIRM = "egcu.org"

# Cas reel
#FIRM = "turbodebt.com"

FIRM_URI = SITE_URI +"/review/"+ FIRM


# CREATION DOSSIER
print("Creation dossier Temp")
folder_file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + "_" + FIRM + "_reviews"
tmp_path = os.path.join(TEMP_FOLDER, folder_file_name)
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

# Effacement du dossier temp
print("#######################################")
print("Suppresion du dossier temp")
shutil.rmtree(tmp_path)


