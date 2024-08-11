#! /usr/bin/python
from elasticsearch import Elasticsearch, helpers
import csv

es = Elasticsearch(
        hosts = "https://localhost:9200",
        basic_auth= ('elastic', 'l4GoiKJ*seV+rcCNz3rC'),
        ca_certs='C:\\Program Files\\elasticsearch-8.15.0\\config\\certs\\http_ca.crt')

# TODO after scrap rationalisation.
mapping = {
    "mappings": {
        "properties": {
            "author_localisation": {"type": "text"},
            "author_name": {"type": "text"},
            "author_url": {"type": "text"},
            "experience_date": {
                "type": "date",
                "format": "dd-MM-yyyy"
            },
            "extract_date": {
                "type": "date",
                "format": "dd-MM-yyyy"
            },
            "firm_name": {
                "type": "text",
                "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                }
            },
            "firm_url": {"type": "text"},
            "note": {"type": "float"},
            "reponse": {"type": "text"},
            "review_date": {
                "type": "date",
                "format": "dd-MM-yyyy"
            },
            "review_title": {"type": "text"},
            "review_url": {"type": "text"},
        }
    }
}

#es.indices.create(index=index_name)#, body=mapping)

def bulk_insert_csv_in_index(file_path, ES_index):
    with open(file_path, encoding='utf-8') as f:
        helpers.bulk(es, csv.DictReader(f), index=ES_index)

bulk_insert_csv_in_index('C:\\tmp\\out\\202408101154_priveeshop.com_reviews.csv', 'reviews_turbodebt')

