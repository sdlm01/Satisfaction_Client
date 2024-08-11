from common import *
from firm_get_all_reviews import firm_get_onePage_reviews
import sys

def manual_firm_get_reviews(page_firm_url, page_list, output_folder, extension="json"):
    """
    ATTENTION: Fonction manuelle, gestion des erreurs minimale.
    Prevu par pour regenerer les fichiers temps des grosses extraction.
    
    Crée un fichier review pour les pages page_list de la firm: page_firm_url
    ecrit le fichier and output_folder

    output_folder est un chemin relatif par rapport au fichier
    Le output_folder doit etre effacé apres coup

    page_firm_url: exemple pour turbodebt.com: https://www.trustpilot.com/review/turbodebt.com

    exemple d'utilisation:
    python3 manual_get_firm_reviews.py https://www.trustpilot.com/review/turbodebt.com [8,34] tmp2 
    """
    for page_number in page_list:
        if page_number == 1:
            url = page_firm_url
        else:
            url = page_firm_url + "?page=" + str(page_number)

        firm_id = page_firm_url.split("/")[-1]
        soup = getPageSoup(url)

        if type(soup) is tuple:
            print ("ERROR:", soup)
        else:
            page_reviews = {"page": page_number, "data": firm_get_onePage_reviews(soup, url)}

            # On ajoute des 0 devant les numero de pages pour le tri
            page_str = str(page_number)
            while len(page_str) < 4:
                page_str = "0" + page_str

            filename = "firm_reviews" + "_" + firm_id + "_" + str(page_str)

            # ecriture json
            to_file(page_reviews,  filename, folder=output_folder, extension=extension)
            print (filename, "Created")

# MAIN
print("manual_firm_get_reviews - START")

# INIT WORKING FOLDER ON SCRIPT FOLDER
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# GET PARAMS

if len(sys.argv) != 4:
    raise Exception("manual_firm_get_reviews - 3 parameters needed: page_firm_url, page_list, output_folder")

page_firm_url = sys.argv[1]
page_list = sys.argv[2]
output_folder = sys.argv[3]

print("manual_firm_get_reviews - Paramteres")
print("page", page_firm_url)
print("page_list", page_list)
print("output_folder", output_folder)

# page_list str to list
page_list = page_list.replace("[","").replace("]","").replace(" ","").split(",")
page_list = [int(x) for x in page_list]

# Creation dir
print("Create directory: " + output_folder)
if output_folder not in os.listdir(os.getcwd()):
    os.makedirs(output_folder)

manual_firm_get_reviews(page_firm_url, page_list, output_folder, extension="json")










