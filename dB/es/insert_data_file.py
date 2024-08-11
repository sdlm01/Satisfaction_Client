#! /usr/bin/python
from elasticsearch import Elasticsearch, helpers
import csv

es = Elasticsearch(
        hosts = "https://localhost:9200",
        basic_auth= ('elastic', 'l4GoiKJ*seV+rcCNz3rC'),
        ca_certs='C:\\Program Files\\elasticsearch-8.15.0\\config\\certs\\http_ca.crt')

def bulk_insert_csv_in_index(file_path, ES_index):
    with open(file_path, encoding='utf-8') as f:
        helpers.bulk(es, csv.DictReader(f), index=ES_index)

bulk_insert_csv_in_index('C:\\tmp\\out\\202408101154_priveeshop.com_reviews.csv', 'reviews_turbodebt')

