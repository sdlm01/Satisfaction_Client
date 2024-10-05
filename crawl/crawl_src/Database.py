from pymongo import MongoClient
from datetime import datetime

class Database:
    def __init__(self, host, port,username,password):
        """Initialisation de la connexion à la base de données MongoDB."""
        try:
            self.client = MongoClient(
                host=host,
                port=int(port),
                username=username,
                password=password
            )
            self.db = self.client.Projet
            print("Connexion réussie à la base de données.")
        except Exception as e:
            print(f"Erreur de connexion à la base de données: {e}")
            self.db = None

    def close(self):
        """Fermeture de la connexion à la base de données."""
        if self.db is not None:
            self.client.close()
            print("Connexion à la base de données fermée.")

    def get_db(self):
        """Récupération de la base de données."""
        return self.db

    def get_firms_list(self):
        """
        Recupere la liste des firms a traiter
        """
        mydb = self.client["Projet"]
        firm_col = mydb["Firms"]

        cursor = firm_col.find({})

        firm_ids = list(cursor)

        return(firm_ids)

    def normalize_review_data(self, review, dt_extract):
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
        date_fields = ['review_date', 'experience_date']
        for field in date_fields:
            if review.get(field):
                try:
                    review[field] = datetime.strptime(review[field], "%Y-%m-%d")
                except ValueError:
                    review[field] = None
            else:
                review[field] = None

        #Extract date
        if isinstance(dt_extract, str):
            review['extract_date'] = dt_extract
        else:
            review['extract_date'] = datetime.strftime(dt_extract, "%Y-%m-%d")

        # Nettoyage des clés vides
        review = {k: v for k, v in review.items() if k}

        return review

    def normalize_firm_data(self, firm, extract_date):
        """
        Normalise et nettoie les données d'une firme avant de les insérer dans MongoDB.
        """
        norm_firm = {}
        norm_firm['firm_name'] = firm.get('name', '').strip() if firm.get('name') else ''
        norm_firm['page_url'] = firm.get('page_url', '').strip() if firm.get('page_url') else ''
        norm_firm['note'] = float(firm.get('note', 0.0)) if firm.get('note') is not None else 0.0
        norm_firm['verified'] = firm.get('verified', False)
        norm_firm['nb_review'] = int(firm.get('nb_review', 0)) if firm.get('nb_review') is not None else 0
        norm_firm['domain'] = firm.get('domain', '').strip() if firm.get('domain') else ''
        norm_firm['subcat'] = firm.get('subcat', [])
        norm_firm['telephone'] = firm.get('telephone', '').strip() if firm.get('telephone') else ''
        norm_firm['mail'] = firm.get('mail', '').strip() if firm.get('mail') else ''
        norm_firm['localisation'] = firm.get('localisation', [])

        try:
            if extract_date is str:
                norm_firm['extract_date'] = datetime.strptime(extract_date, "%Y-%m-%d")
            else:
                norm_firm['extract_date'] = datetime.strftime(extract_date, "%Y-%m-%d")

        except ValueError:
            norm_firm['extract_date'] = None

        return norm_firm
    
    def insert_firmInfos(self, data, dt_extract):
        #self.collection = self.db.Firms
        try:
            firm = self.normalize_firm_data(data, dt_extract)
            # On s'assure que la firme est insérée ou mise à jour sans créer de doublons
            self.db.Firms.update_one(
                {"page_url": data.get('page_url')}, 
                {"$set": data}, 
                upsert=True
            )
            print("Insertion des firmesInfo réussie.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des firmesInfo: {e}")


    def insert_review(self, reviews, dt_extract, new_dt_extract):

        #self.collection = self.db.Reviews
        try:
            for review in reviews:

                review = self.normalize_review_data(review, new_dt_extract)
                # Validation des champs essentiels avant insertion
                if review and isinstance(review, dict) and "review_url" in review:
                    # On évite les doublons en utilisant review_url comme clé unique
                    self.db.Reviews.update_one(
                        {"review_url": review.get('review_url')},
                        {"$set": review},
                        upsert=True
                    )
                else:
                    print(f"Avis vide ou mal formé : {review}")
            print("Insertion des avis réussie.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des avis: {e}")