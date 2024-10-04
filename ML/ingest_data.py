from elasticsearch import Elasticsearch, helpers
import csv

es = Elasticsearch(hosts = "http://@localhost:9200")

with open('all_reviews_egcu.org.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    helpers.bulk(es, reader, index='egcu')
