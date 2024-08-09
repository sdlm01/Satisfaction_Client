#!/usr/bin/python
from elasticsearch import Elasticsearch
import json
import warnings
import os
warnings.filterwarnings("ignore")

# Connexion au cluster Elasticsearch
client = Elasticsearch(hosts="http://localhost:9200")

def execute_query(question_number, query):
    """
    Exécute une requête Elasticsearch et enregistre la requête et la réponse dans des fichiers JSON.
    
    :param question_number: Le numéro de la question pour identifier les fichiers de sortie.
    :param query: La requête Elasticsearch sous forme de dictionnaire Python.
    """
    response = client.search(index="eval", body=query)
  
    # Vérifie que le répertoire existe, sinon le crée
    os.makedirs("./eval/", exist_ok=True)

    # Sauvegarde de la réponse dans un fichier json
    with open(f"./eval/q_{question_number}_response.json", "w") as f:
        json.dump(dict(response), f, indent=2)

    # Sauvegarde de la requête dans un fichier json
    with open(f"./eval/q_{question_number}_request.json", "w") as f:
        json.dump(query, f, indent=2)

def main():
    # Distribution des avis par score de satisfaction
    query_1 = {
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
    # Requête 2 : Nombre total d'avis par entreprise ou par sous-catégorie
    query_2 = {
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
    # Requête 3 : Sentiment général des avis
    query_3 = {
        "size": 0,
        "aggs": {
            "sentiment_distribution": {
                "terms": {
                    "script": """
                    if (doc['note'].value >= 4) {
                        return 'positif';
                    } else if (doc['note'].value >= 2) {
                        return 'neutre';
                    } else {
                        return 'negatif';
                    }
                    """,
                    "size": 3
                }
            }
        }
    }
    # Requête 4 : Mots ou phrases fréquemment mentionnés dans les avis positifs/négatifs
    query_4_positive = {
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
    query_4_negative = {
        "size": 0,
        "query": {
            "range": {
                "note": {
                  "lt": 20
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
    """query_merch = {}
{"size":0,"query":{"range":{"note":{"gte":4}}},"aggs":{"frequent_words":{"terms":{"field":"review_title.keyword","size":20}}}}
{}
{"size":0,"query":{"range":{"note":{"lt":20}}},"aggs":{"frequent_words":{"terms":{"field":"review_title.keyword","size":20}}}}"""

    # Requête 5 : Évolution des avis au fil du temps
    query_5 = {
        "size": 0,
        "aggs": {
            "reviews_over_time": {
                "date_histogram": {
                    "field": "review_date",
                    "calendar_interval": "month"
                }
            }
        }
    }
    # Requête 6 : Pics ou baisses significatives dans le volume des avis
    query_6 = {
        "size": 0,
        "aggs": {
            "volume_changes": {
                "date_histogram": {
                    "field": "review_date",
                    "calendar_interval": "month"
                },
                "aggs": {
                    "review_volume": {
                        "value_count": {
                            "field": "review_title.keyword"
                        }
                    }
                }
            }
        }
    }
    # Requête 7 : Segmentation par localisation
    query_7 = {
        "size": 0,
        "aggs": {
            "reviews_by_location": {
                "terms": {
                    "field": "author_localisation.keyword",
                    "size": 10
                }
            }
        }
    }
    # Requête 8 : Différences significatives entre zone en termes de satisfaction des clients
    query_8 = {
        "size": 0,
        "aggs": {
            "satisfaction_by_department": {
                "terms": {
                    "field": "subcat.keyword",
                    "size": 10
                },
                "aggs": {
                    "average_satisfaction": {
                        "avg": {
                            "field": "note"
                        }
                    }
                }
            }
        }
    }
    # Requête 9 : Identification des problèmes courants
    query_9 = {
        "query": {
            "range": {
                "note": {"lt": 2}
            }
        },
        "aggs": {
            "common_problems": {
                "terms": {
                    "field": "review_title.keyword",
                    "size": 20
                }
            }
        }
    }
    # Requête 10 : Suggestions d'amélioration
    query_10 = {
        "query": {
            "range": {
                "note": {"lt": 2}
            }
        },
        "aggs": {
            "improvement_suggestions": {
                "terms": {
                    "field": "reponse.keyword",
                    "size": 20
                }
            }
        }
    }
    # Requête 11 : Évolution des avis après mise en œuvre de mesures correctives
    query_11 = {
        "size": 0,
        "query": {
            "range": {
                "review_date": {
                    "gte": "now-6M/M",
                    "lt": "now/M"
                }
            }
        },
        "aggs": {
            "reviews_last_6_months": {
                "date_histogram": {
                    "field": "review_date",
                    "calendar_interval": "month"
                },
                "aggs": {
                    "average_note": {
                        "avg": {
                            "field": "note"
                        }
                    }
                }
            }
        }
    }
    # Requête 12 : Amélioration notable après interventions spécifiques
    query_12 = {
  "size": 0,
  "query": {
    "bool": {
      "should": [
        {
          "range": {
            "review_date": {
              "gte": "now-6M/M",
              "lt": "now/M"
            }
          }
        },
        {
          "range": {
            "review_date": {
              "gte": "now-12M/M",
              "lt": "now-6M/M"
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "reviews_comparison": {
      "date_histogram": {
        "field": "review_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "average_note": {
          "avg": {
            "field": "note"
          }
        }
      }
    }
  }
}

    # Liste des queries avec leurs numéros de question
    queries = [
        ("1", query_1),
        ("2", query_2),
        ("3", query_3),
        ("4_positive", query_4_positive),
        ("4_negative", query_4_negative),
        ("5", query_5),
        ("6", query_6),
        ("7", query_7),
        ("8", query_8),
        ("9", query_9),
        ("10", query_10),
        ("11", query_11),
        ("12", query_12),
    ]

    # Exécution des requêtes
    for question_number, query in queries:
        execute_query(question_number, query)

if __name__ == "__main__":
    main()
