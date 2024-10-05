#! /usr/bin/python
from elasticsearch import Elasticsearch
import json
import warnings
import warnings
warnings.filterwarnings("ignore")
# Connexion au cluster
client = Elasticsearch(hosts = "http://@localhost:9200")

questions = []
question_1 = "Distribution des avis par score de satisfaction"
query1 ={
        "size": 0,
        "aggs": {
            "satisfaction_distribution": {
                "terms": {
                    "field": "note",
                    "size": 5
                }
            }
        }
    }
question_2 = "Nombre total d'avis par entreprise ou par sous-catégorie"
query2 ={
        "size": 0,
        "aggs": {
            "total_reviews_by_firm": {
                "terms": {
                    "field": "firm_name.keyword",  
                    "size": 10
                }
            },
            "total_reviews_by_subcat": {
                "terms": {
                    "field": "subcat.keyword",  
                    "size": 10
                }
            }
        }
    }
question_3 = "Mots ou phrases fréquemment mentionnés dans les avis positifs"
query3 = {
    "size": 0,
    "query": {
        "range": {
            "note": {
                "gte": 4
            }
        }
    },
    "aggs": {
        "frequent_words": {
            "terms": {
                "field": "review_title.keyword", 
                "size": 20
            }
        }
    }
}
question_4 = "Mots ou phrases fréquemment mentionnés dans les avis négatifs"
query4 = {
        "size": 0,
        "query": {
            "range": {
                "note": {
                  "lte": 3
                }
            }
        },
        "aggs": {
            "frequent_words": {
                "terms": {
                    "field": "review_title.keyword",
                    "size": 20
                }
            }
        }
    }
liste = []
liste.append(query1)
liste.append(query2)
liste.append(query3)
liste.append(query4)

questions.append(question_1)
questions.append(question_2)
questions.append(question_3)
questions.append(question_4)

for i, e in zip(questions,liste):
    response = client.search(index="test_final_new", body=e)
    # Sauvegarde de la requête et la réponse dans un fichier json
    with open("./{}.json".format("request"), "a") as f:
        f.write(f"requete: {i}")
        json.dump(dict(e), f, indent=4)
        f.write(f"\n")
        f.write(f"resultat:")
        json.dump(dict(response), f, indent=4)
        f.write(f"\n")

