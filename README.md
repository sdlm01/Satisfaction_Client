Projet : Analyse de la Satisfaction Client dans la Supply Chain

Contexte
Ce projet s'inscrit dans le cadre du cursus Data Engineer et vise à analyser la satisfaction des clients pour différents produits et services. L'objectif est de comprendre comment les entreprises, via leurs chaînes d'approvisionnement, répondent aux attentes des clients, en se basant sur des avis collectés sur des plateformes comme Trustpilot.

Objectifs du projet
- Récolte de données : Utilisation du web scraping pour extraire des avis clients et des informations sur les entreprises à partir de sources publiques.
- Organisation des données : Création d'une base de données relationnelle (PostgreSQL) et d'une base orientée documents (MongoDB) pour stocker les avis clients. Mise en place d'un dashboard Kibana pour visualiser et analyser les données.
- Analyse de sentiment : Implémentation de techniques de Machine Learning pour analyser les sentiments exprimés dans les avis.
- API et déploiement : Création d'une API (FastAPI) pour rendre les analyses disponibles via un service web, avec une infrastructure dockerisée prête pour la production.
- Automatisation et monitoring : Mise en place d'un cronjob et d'une surveillance de l'application via Prometheus et Grafana.

Étapes clés
- Web Scraping : Extraction de données à partir de Trustpilot pour obtenir des avis détaillés et des informations sur les entreprises.
- Base de données : Organisation des données en tables PostgreSQL et MongoDB pour permettre des requêtes rapides et efficaces.
- Dashboard Kibana : Visualisation des résultats et des avis clients.
- Analyse de sentiment : Utilisation de modèles de Machine Learning pour classifier les avis selon leur tonalité.
- API et Docker : Exposition des résultats via une API et déploiement avec Docker et Docker-Compose.
- Automatisation : Mise en place d'une automatisation quotidienne des tâches avec un Cronjob et monitoring avec Prometheus/Grafana.

Technologies utilisées
Python, Pandas, Scikit-learn
PostgreSQL, MongoDB, ElasticSearch
FastAPI
Docker, Docker-Compose
Cronjob, Prometheus, Grafana

Résultats attendus
Une infrastructure complète pour la collecte, l'analyse, et la visualisation de la satisfaction client, avec des possibilités d'extension et de déploiement en production.

Déploiement
Le projet est entièrement dockerisé et peut être mis en production via Docker et Docker-Compose. Les flux de données et les modèles sont automatisés et un cronjob a été mis en place pour les mises à jour futures.
