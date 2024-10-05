from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import bulk, BulkIndexError 
import csv
import os 

es = Elasticsearch(hosts = "http://@localhost:9200", timeout=3000000)

# Définir le nom de l'index
index_name = "test_final"

# Définir le mapping pour l'index
mapping = {
    "mappings": {
        "properties": {
            "author_localisation": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "author_name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "author_url": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "experience_date": {
                "type": "date",
                "format": "yyyy-MM-dd"
            },
            "extract_date": {
                "type": "date",
                "format": "yyyy-MM-dd"
            },
            "firm_id": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "firm_name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "note": {
                "type": "float"
            },
            "reponse": {
                "type": "boolean"
            },
            "review_date": {
                "type": "date"
            },
            "review_text": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "review_title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "review_url": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "sentiments": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }
        }
    }
}

# Créer l'index
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)
    print(f"L'index '{index_name}' a été créé avec succès.")
else:
    print(f"L'index '{index_name}' existe déjà.")

# Supprimer tous les documents existants dans l'index
es.delete_by_query(index=index_name, body={"query": {"match_all": {}}})

# Lire le fichier CSV et indexer les nouveaux documents
with open(f"{os.path.dirname(os.getcwd())}/data_final.csv") as f:
    reader = csv.DictReader(f)
    
    try:
        helpers.bulk(es, reader, index=index_name)
        print("Documents ajoutés avec succès.")
    except BulkIndexError as e:
        print(f"Erreur lors de l'indexation : {e.errors}")




