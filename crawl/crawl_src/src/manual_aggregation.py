from ..common import fileAggregation
from ..firm_get_all_reviews import firm_get_onePage_reviews
import sys
import os
import pandas as pd

def agg_file_to_one_csv_json(FOLDER_IN,FOLDER_OUT,FILE_NAME, file_type_in="csv", file_type_out="csv", line_limit=500000):
    """
    aggrege des fichier csv ou json dans un csv
    ATTENTION: seulement testé avec json en entrée
    :param FOLDER_IN: folder contenant les csv
    :param FOLDER_OUT: folder de sortie
    :param FILE_NAME: nom du fichier SANS extension
    :param file_type_in: defaut "csv" extension des fichiers a aggreger. autre valeur utile= "json"
    :param file_type_out: defaut "csv" extension des fichiers a aggreger.
        autre valeur utile= "json", "both" : genere csv et json

    :return:
    """
    file_list = os.listdir(FOLDER_IN)

    if file_list == 0:
        raise Exception("agg_csv_file - No file in ", FOLDER_IN)
    else:

        df_all = pd.DataFrame(index=None)
        file_list_filtered = []

        # selection des fichiers selon letype attendu
        for file in file_list:
            if "."+file_type_in in file:
                file_list_filtered.append(os.path.join(FOLDER_IN,file))

        step = 0
        file_num = 1
        for file in file_list_filtered:
            print("file treated: ", file)
            # try except pour eviter une erreur lorsque le ficheir est vide (par exemple). Ignore le fichier.
            readOk=True
            try:
                if file_type_in == "csv":
                    tmpFile = pd.read_csv(file, index_col=False)
                elif file_type_in == "json":
                    tmpFile = pd.read_json(file)
            except:
                readOk = False

            if readOk:
                df_all = pd.concat([df_all, tmpFile], ignore_index=True)
                if len(df_all) >= line_limit:
                    print("File limit Exceeded")
                    # on enregistre le fichier et on repars sur un df_all vide pour soulager la ram
                    new_file_name = FILE_NAME + "_" + str(file_num)

                    try:
                        if file_type_out == "csv":
                            df_all.to_csv(os.path.join(FOLDER_OUT, new_file_name + ".csv"), header=True, index=False)
                        elif file_type_out == "json":
                            df_all.to_json(os.path.join(FOLDER_OUT, new_file_name + ".json"), orient="records")
                        elif file_type_out == "both":
                            df_all.to_csv(os.path.join(FOLDER_OUT, new_file_name + ".csv"), header=True, index=False)
                            df_all.to_json(os.path.join(FOLDER_OUT, new_file_name + ".json"), orient="records", lines=True)
                    except Exception as e:
                        raise("ERROR writing out file", repr(e))

                    # clear df_all update variables
                    df_all = pd.DataFrame(index=None)
                    file_num += 1


                print("df_all len: ", len(df_all))
            else:
                continue
        # on print le restant de df_all ou df_all si line_limit n'est jamais atteinte
        if file_num == 1: # un seul fichier on ne modifie pas le file_name
            new_file_name = FILE_NAME
        else:
            new_file_name = FILE_NAME + "_" + str(file_num)

        try:
            if file_type_out == "csv":
                df_all.to_csv(os.path.join(FOLDER_OUT, new_file_name + ".csv"), header=True, index=False)
            elif file_type_out == "json":
                df_all.to_json(os.path.join(FOLDER_OUT, new_file_name + ".json"), orient="records")
            elif file_type_out == "both":
                df_all.to_csv(os.path.join(FOLDER_OUT, new_file_name + ".csv"), header=True, index=False)
                df_all.to_json(os.path.join(FOLDER_OUT, new_file_name + ".json"), orient="records", lines=True)
        except Exception as e:
            raise ("ERROR writing out file", repr(e))




FOLDER_IN = "C:\\tmp\\out\\investment_wealth\\allready_aggregated\\"
FOLDER_OUT = "C:\\tmp\\out\\investment_wealth\\"

# filename sans extension
FILE_NAME = "all_reviews_2024-09-10"

agg_file_to_one_csv_json(FOLDER_IN, FOLDER_OUT, FILE_NAME, file_type_in="csv", file_type_out="csv")
