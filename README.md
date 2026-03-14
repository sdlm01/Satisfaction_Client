# Pipeline ETL & NLP — Analyse de la Satisfaction Client
> Projet de fin de cursus **Data Engineer** (Mines ParisTech / Datascientest) — réalisé en équipe.

Pipeline complet d'ingestion, de traitement et de visualisation d'avis clients scrappés sur Trustpilot, avec un modèle NLP de classification de sentiment et un monitoring en temps réel.


## Chiffres clés
| Métrique | Valeur |
|---|---|
| Avis scrappés | **219 992** |
| Entreprises couvertes | **507** |
| Accuracy du modèle NLP | **73 %** |
| Services Docker orchestrés | **2** |
| Fréquence d'exécution | **Quotidienne** (Cronjob) |

## Architecture du pipeline
```
Trustpilot (Web)
       │
       ▼
   Scraping Python (BeautifulSoup)
       │
       ├──▶ MongoDB (données brutes)
       ├──▶ PostgreSQL (données structurées)
       └──▶ Elasticsearch (indexation full-text)
               │
               ▼
         Modèle NLP (Scikit-learn)
         Classification de sentiment
               │
               ├──▶ FastAPI (exposition API)
               └──▶ Kibana (dashboard temps réel)
                       │
               Prometheus / Grafana
               (monitoring & alerting)
```

## Stack technique
| Composant | Technologie |
|---|---|
| Scraping | Python, BeautifulSoup |
| Stockage | PostgreSQL, MongoDB, Elasticsearch |
| Machine Learning | Scikit-learn (classification NLP) |
| API | FastAPI |
| Conteneurisation | Docker, Docker Compose |
| Visualisation | Kibana |
| Monitoring | Prometheus, Grafana |
| Automatisation | Cronjob, Shell |

## Structure du projet
```
.
├── crawl/                  # Scripts de web scraping Trustpilot
├── ML/                     # Modèle NLP de classification de sentiment
├── psgr/                   # Scripts PostgreSQL (schéma, ingestion)
├── mongodb/                # Scripts MongoDB (ingestion données brutes)
├── elasticsearch/          # Configuration Elasticsearch + mapping
├── fast_api/               # API FastAPI pour exposition des prédictions
├── prometheus-grafana/     # Configuration monitoring
├── cronjobs/               # Automatisation quotidienne
├── docker-compose.yml      # Orchestration des services
├── restart_services.sh     # Script de redémarrage des services
└── README.md
```

## Fonctionnalités
**Ingestion multi-sources** — Extraction automatisée des avis Trustpilot via scraping, avec stockage parallèle dans trois bases de données complémentaires (MongoDB pour le brut, PostgreSQL pour le structuré, Elasticsearch pour la recherche full-text).

**Classification NLP** — Modèle de Machine Learning entraîné sur les avis textuels pour prédire automatiquement le niveau de satisfaction client (accuracy : 73 %).

**Dashboard temps réel** — Visualisation Kibana des indicateurs de satisfaction, avec suivi de la dérive du modèle dans le temps.

**Monitoring** — Prometheus et Grafana pour le suivi des performances du pipeline et des services.

**Automatisation** — Exécution quotidienne automatique via Cronjob : scraping, ingestion, prédiction, mise à jour du dashboard.

## Lancement
```bash
# Cloner le repo
git clone https://github.com/sdlm01/Satisfaction_Client.git
cd Satisfaction_Client

# Lancer les services
docker-compose up -d
```

## Auteurs
Projet réalisé en équipe dans le cadre du cursus Data Engineer — Mines ParisTech / Datascientest (2024).

Projet réalisé en équipe dans le cadre du cursus Data Engineer — Mines ParisTech / Datascientest (2024).
                       ▼
