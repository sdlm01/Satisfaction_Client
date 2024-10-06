Projet : Analyse de la Satisfaction Client 

Contexte :
Ce projet s'inscrit dans le cadre du cursus Data Engineer et vise à analyser la satisfaction des clients pour différents produits et services en se basant sur des avis collectés sur des plateformes comme Trustpilot.

Objectifs du projet :
•	Analyse automatique de la satisfaction client via la prédiction d’un modèle NLP sur la base d’un avis textuel
•	Mise à disposition via une API de l’application
•	Suivi de la dérive du modèle de prédiction dans le temps

Étapes clés :
•	Web Scraping : Extraction de données à partir de Trustpilot 
•	Ingestion de données sous Mongo DB, PostgreSQL, Elastic Search
•	Analyse de sentiment : Utilisation de modèles de Machine Learning pour classifier les avis selon leur satisfaction client.
•	Dashboard Kibana : Visualisation des résultats, des avis clients et suivi de la dérive au cours du temps
•	API et Docker : Exposition des résultats via une API et déploiement avec Docker 
•	Automatisation : Mise en place d'une automatisation quotidienne des tâches avec un Cronjob et monitoring avec Prometheus/Grafana.

Technologies utilisées :
 Python, Pandas, Scikit-learn, PostgreSQL, MongoDB, ElasticSearch ,FastAPI, Docker, Cronjob, Shell, Prometheus, Grafana, Kibana
