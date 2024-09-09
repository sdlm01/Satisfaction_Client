from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import bulk, BulkIndexError 
import csv
import os 

es = Elasticsearch(hosts = "http://@localhost:9200", timeout=3000000)

with open(f"{os.path.dirname(os.getcwd())}/data_final.csv") as f:
    reader = csv.DictReader(f)

        #helpers.bulk(es, reader, index='test_final')
    try:
        helpers.bulk(es, reader, index='test_final')
    except BulkIndexError as e:
        print(f"{e.errors}")
        



