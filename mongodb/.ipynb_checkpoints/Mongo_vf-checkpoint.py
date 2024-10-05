#Mongo_vf.py

import json
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
import csv
import sys 
import os
#Insertion de données sur Postgresql
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from psgr.Postgresql_vf import insert_into_postgresql


# === UTILITAIRES === #

def normalize_data(review):
    """
    Normalisez et nettoyez les données avant de les insérer dans MongoDB.
    Gérez les valeurs NaN, NULL et assurez un formatage cohérent.
    """
    review['firm_name'] = review.get('firm_name', '').strip() if review.get('firm_name') else ''
    review['review_title'] = review.get('review_title', '').strip() if review.get('review_title') else ''
    review['review_text'] = review.get('review_text', '').strip() if review.get('review_text') else ''
    review['note'] = float(review.get('note', 0.0)) if review.get('note') is not None else 0.0
    review['author_name'] = review.get('author_name', '').strip() if review.get('author_name') else ''
    review['author_localisation'] = review.get('author_localisation', '').strip() if review.get('author_localisation') else ''
    review['reponse'] = review.get('reponse', 'False')

    # Vérification des dates
    date_fields = ['review_date', 'experience_date', 'extract_date']
    for field in date_fields:
        if review.get(field):
            try:
                review[field] = datetime.strptime(review[field], "%Y-%m-%d")
            except ValueError:
                review[field] = None
        else:
            review[field] = None

    # Nettoyage des clés vides
    review = {k: v for k, v in review.items() if k}

    return review


def normalize_firm_data(firm):
    """
    Normalise et nettoie les données d'une firme avant de les insérer dans MongoDB.
    """
    firm['firm_name'] = firm.get('name', '').strip() if firm.get('name') else ''
    firm['page_url'] = firm.get('page_url', '').strip() if firm.get('page_url') else ''
    firm['note'] = float(firm.get('note', 0.0)) if firm.get('note') is not None else 0.0
    firm['verified'] = firm.get('verified', False)
    firm['nb_review'] = int(firm.get('nb_review', 0)) if firm.get('nb_review') is not None else 0
    firm['domain'] = firm.get('domain', '').strip() if firm.get('domain') else ''
    firm['subcat'] = firm.get('subcat', [])
    firm['telephone'] = firm.get('telephone', '').strip() if firm.get('telephone') else ''
    firm['mail'] = firm.get('mail', '').strip() if firm.get('mail') else ''
    firm['localisation'] = firm.get('localisation', [])

    try:
        firm['extract_date'] = datetime.strptime(firm.get('extract_date', ''), "%Y-%m-%d") if firm.get('extract_date') else None
    except ValueError:
        firm['extract_date'] = None

    return firm

def json_serial(obj):
    """Fonction de sérialisation pour JSON pour gérer les types non serializables (datetime, ObjectId)."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} non sérialisable")


# === GESTION BASE DE DONNÉES === #

class Database:
    def __init__(self):
        """Initialisation de la connexion à la base de données MongoDB."""
        try:
            self.client = MongoClient(
                host="my_mongo_server",
                port=27017,
                username="datascientest",
                password="dst123"
            )
            self.db = self.client.Projet
            print("Connexion réussie à la base de données.")
        except Exception as e:
            print(f"Erreur de connexion à la base de données: {e}")
            self.db = None

    def create_indexes(self):
        """Création des index pour les collections Firms et Reviews."""
        if self.db is not None:
            self.db.Firms.create_index([("firm_name", ASCENDING)], unique=True)
            self.db.Firms.create_index([("page_url", ASCENDING)], unique=True)
            self.db.Reviews.create_index([("firm_id", ASCENDING)])
            self.db.Reviews.create_index([("review_url", ASCENDING)], unique=True)
            self.db.Reviews.create_index([("review_date", DESCENDING)])
            print("Index créés avec succès.")

    def close(self):
        """Fermeture de la connexion à la base de données."""
        if self.db is not None:
            self.client.close()
            print("Connexion à la base de données fermée.")

    def get_db(self):
        """Récupération de la base de données."""
        return self.db

# === COLLECTION FIRMS === #

class FirmsCollection:
    def __init__(self, db):
        """Initialisation de la collection Firms."""
        self.collection = db.Firms

    def insert_firm_data_json(self, json_file_path):
        """Insertion des firmes à partir d'un fichier JSON."""
        try:
            with open(json_file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)

            for firm in data:
                firm = normalize_firm_data(firm)
                # On s'assure que la firme est insérée ou mise à jour sans créer de doublons
                self.collection.update_one(
                    {"page_url": firm.get('page_url')}, 
                    {"$set": firm}, 
                    upsert=True
                )
            print("Insertion des firmes réussie.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des firmes: {e}")

    def find_firm_by_name(self, firm_name):
        """Rechercher une firme par son nom."""
        return self.collection.find_one({"firm_name": firm_name})


# === COLLECTION REVIEWS === #

class ReviewsCollection:
    def __init__(self, db):
        """Initialisation de la collection Reviews."""
        self.collection = db.Reviews

    def insert_scraped_data_json(self, json_file_path):
        """Insertion des avis à partir d'un fichier JSON."""
        try:
            with open(json_file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)

            for review in data:
                review = normalize_data(review)

                # Affichage du contenu de la donnée pour débogage
                print(f"Review normalisé : {review}")

                # Validation des champs essentiels avant insertion
                if review and isinstance(review, dict) and "review_url" in review:
                    # On évite les doublons en utilisant review_url comme clé unique
                    self.collection.update_one(
                        {"review_url": review.get('review_url')},
                        {"$set": review},
                        upsert=True
                    )
                else:
                    print(f"Avis vide ou mal formé : {review}")
            print("Insertion des avis réussie.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des avis: {e}")



    def get_firms_with_reviews(self):
        """Récupérer toutes les firmes avec leurs avis via une agrégation $lookup."""
        pipeline = [
            {
                "$lookup": {
                    "from": "Firms",  # Nom de la collection des firmes
                    "localField": "firm_id",  # Clé locale dans les avis (Reviews)
                    "foreignField": "firm_id",  # Clé dans les firmes (Firms)
                    "as": "firm_info"  # Nom de la clé où la firme sera stockée
                }
            },
            {
                "$unwind": "$firm_info"  # Décompose le tableau des firmes (une seule firme par avis)
            }
        ]

        # Exécuter l'agrégation et afficher les résultats pour débogage
        results = list(self.collection.aggregate(pipeline))
        print(f"Nombre de firmes avec avis récupérées : {len(results)}")
        
        # Affichage des résultats pour voir les données
        for result in results:
            print(result)

        return results



    def export_firms_with_reviews_to_json(self, file_path):
        """Exporter les firmes avec leurs avis dans un fichier JSON."""
        firms_with_reviews = self.get_firms_with_reviews()
        
        if len(firms_with_reviews) == 0:
            print("Aucune firme avec avis n'a été trouvée.")
            return

        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(firms_with_reviews, file, default=json_serial, ensure_ascii=False, indent=4)
            print(f"Données exportées avec succès dans {file_path}")
        except Exception as e:
            print(f"Erreur lors de l'exportation des données : {e}")

# === EXPORTATION EN CSV === #
def export_firms_with_reviews_to_csv(self, file_path):
    """Exporter les firmes avec leurs avis dans un fichier CSV."""
    firms_with_reviews = self.get_firms_with_reviews()

    if len(firms_with_reviews) == 0:
        print("Aucune firme avec avis n'a été trouvée.")
        return

    try:
        # Ouvrir le fichier en mode écriture
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Écrire l'en-tête du fichier CSV
            writer.writerow([
                'firm_name', 'page_url', 'firm_note', 'firm_verified', 'firm_nb_review', 'firm_domain', 'review_title', 
                'review_text', 'review_note', 'review_author', 'review_date', 'review_url'
            ])

            # Écrire les données dans le fichier CSV
            for item in firms_with_reviews:
                firm_info = item.get('firm_info', {})
                writer.writerow([
                    firm_info.get('firm_name', ''),
                    firm_info.get('page_url', ''),
                    firm_info.get('note', ''),
                    firm_info.get('verified', ''),
                    firm_info.get('nb_review', ''),
                    firm_info.get('domain', ''),
                    item.get('review_title', ''),
                    item.get('review_text', ''),
                    item.get('note', ''),
                    item.get('author_name', ''),
                    item.get('review_date', ''),
                    item.get('review_url', '')
                ])

        print(f"Données exportées avec succès dans {file_path}")
    except Exception as e:
        print(f"Erreur lors de l'exportation en CSV : {e}")


# === SCRIPT PRINCIPAL === #
def main():
    # Initialisation de la base de données
    db = Database()
    database = db.get_db()
    if database is None:
        return

    # Création des index
    db.create_indexes()

    # Insertion des données depuis les fichiers JSON
    firms = FirmsCollection(database)
    reviews = ReviewsCollection(database)

    firms.insert_firm_data_json("/app/mongodb/Firms_infos.json")
    reviews.insert_scraped_data_json("/app/mongodb/debt_relief_service_raw_reviews_COMPLETE.json")

    # Exportation des firmes et leurs avis dans un fichier JSON
    reviews.export_firms_with_reviews_to_json("/app/mongodb/firms_with_reviews.json")
    #reviews.export_firms_with_reviews_to_csv("/app/firms_with_reviews.csv")
    
    firms_with_reviews = reviews.get_firms_with_reviews()

    # Insérer les firmes et avis dans PostgreSQL
    insert_into_postgresql(firms_with_reviews)

    # Fermeture de la connexion à la base de données
    db.close()


if __name__ == "__main__":
    main()