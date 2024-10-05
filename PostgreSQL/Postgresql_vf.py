import psycopg2
import json
from datetime import datetime
import time
BATCH_SIZE = 100  # Taille du batch pour la gestion de la volumétrie

def create_tables(conn):
    """Créer les tables Firms, Firm_Star_Percs, Firm_Subcategories, Authors et Reviews si elles n'existent pas."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS Firms (
            firm_id SERIAL PRIMARY KEY,
            firm_name VARCHAR NOT NULL UNIQUE,
            firm_url VARCHAR,
            domain VARCHAR,
            nb_review INTEGER,
            note FLOAT,
            telephone VARCHAR,
            mail VARCHAR,
            verified BOOLEAN,
            extract_date TIMESTAMP,
            localisation TEXT[]
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Firm_Star_Percs (
            firm_id INTEGER REFERENCES Firms(firm_id) ON DELETE CASCADE,
            star_value INTEGER,
            percentage INTEGER,
            PRIMARY KEY (firm_id, star_value)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Firm_Subcategories (
            firm_id INTEGER REFERENCES Firms(firm_id) ON DELETE CASCADE,
            subcategory_name VARCHAR,
            PRIMARY KEY (firm_id, subcategory_name)
        );
        """
    ]

    try:
        cursor = conn.cursor()
        for query in queries:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        print("Tables créées avec succès.")
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la création des tables : {e}")

def insert_into_postgresql(firms_with_reviews):
    """Insertion des données MongoDB dans PostgreSQL avec gestion des erreurs et insertion par batch."""
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            database="dst_db",
            user="daniel",
            password="datascientest",
            host="pg_container",
            port="5432"
        )
        cursor = conn.cursor()
        print("Connexion réussie à PostgreSQL.")

        # Gestion par batch
        for i in range(0, len(firms_with_reviews), BATCH_SIZE):
            batch = firms_with_reviews[i:i + BATCH_SIZE]
            print(f"Insertion du batch {i // BATCH_SIZE + 1} / {len(firms_with_reviews) // BATCH_SIZE + 1}")

            for firm in batch:
                firm_info = firm['firm_info']

                # Insertion des firmes
                try:
                    cursor.execute("""
                        INSERT INTO Firms (firm_name, firm_url, domain, nb_review, note, telephone, mail, verified, extract_date, localisation)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (firm_name) DO UPDATE
                        SET firm_url = EXCLUDED.firm_url,
                            domain = EXCLUDED.domain,
                            nb_review = EXCLUDED.nb_review,
                            note = EXCLUDED.note,
                            telephone = EXCLUDED.telephone,
                            mail = EXCLUDED.mail,
                            verified = EXCLUDED.verified,
                            extract_date = EXCLUDED.extract_date,
                            localisation = EXCLUDED.localisation
                        RETURNING firm_id;
                    """, (
                        firm_info['firm_name'],
                        firm_info['page_url'],
                        firm_info['domain'],
                        firm_info['nb_review'],
                        firm_info['note'],
                        firm_info['telephone'],
                        firm_info['mail'],
                        firm_info['verified'],
                        firm_info['extract_date'],
                        firm_info['localisation']
                    ))

                    firm_id = cursor.fetchone()[0]
                    print(f"Firme insérée avec succès, firm_id: {firm_id}")
                except Exception as e:
                    print(f"Erreur lors de l'insertion de la firme : {e}")
                    conn.rollback()  # Annuler cette transaction
                    continue  # Passer à la firme suivante

                # Insertion des pourcentages d'étoiles
                try:
                    for star_value, percentage in firm_info['firm_star_percs'].items():
                        cursor.execute("""
                            INSERT INTO Firm_Star_Percs (firm_id, star_value, percentage)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (firm_id, star_value, percentage))
                    print(f"Pourcentages d'étoiles insérés pour firm_id: {firm_id}")
                except Exception as e:
                    print(f"Erreur lors de l'insertion des pourcentages d'étoiles : {e}")
                    conn.rollback()  # Annuler la transaction si cette partie échoue

                # Insertion des sous-catégories
                try:
                    for subcat in firm_info['subcat']:
                        cursor.execute("""
                            INSERT INTO Firm_Subcategories (firm_id, subcategory_name)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (firm_id, subcat))
                    print(f"Sous-catégories insérées pour firm_id: {firm_id}")
                except Exception as e:
                    print(f"Erreur lors de l'insertion des sous-catégories : {e}")
                    conn.rollback()  # Annuler cette transaction

            # Commit des données pour ce batch
            conn.commit()
            print(f"Batch {i // BATCH_SIZE + 1} inséré avec succès.")

        cursor.close()
        conn.close()
        print("Toutes les données ont été insérées avec succès dans PostgreSQL.")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans PostgreSQL : {e}")

# Fonction générique d'exécution de requêtes avec ou sans résultats
def execute_query(conn, query, params=None):
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall() if cur.description else None
        conn.commit()
        cur.close()
        return results
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'exécution de la requête: {e}")
        return None

#Requêtes SQL
def count_firms_per_subcategory(conn):
    """
    Compter le nombre de firmes pour chaque sous-catégorie.
    """
    query = """
    SELECT 
        fc.subcategory_name, 
        COUNT(f.firm_id) AS firm_count
    FROM Firm_Subcategories fc
    JOIN Firms f ON fc.firm_id = f.firm_id
    GROUP BY fc.subcategory_name
    ORDER BY firm_count DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_with_high_ratings(conn, min_rating):
    """
    Obtenir les firmes ayant une note supérieure à un certain seuil.
    """
    query = """
    SELECT 
        firm_name, 
        note, 
        nb_review 
    FROM Firms 
    WHERE note > %s
    ORDER BY note DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query, (min_rating,))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_by_review_count_range(conn, min_reviews, max_reviews):
    """
    Obtenir les firmes avec un nombre d'avis compris entre une plage.
    """
    query = """
    SELECT 
        firm_name, 
        nb_review, 
        note 
    FROM Firms 
    WHERE nb_review BETWEEN %s AND %s
    ORDER BY nb_review DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query, (min_reviews, max_reviews))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_most_recent_firms(conn, limit=10):
    """
    Récupérer les firmes extraites récemment, limité à un certain nombre.
    """
    query = """
    SELECT 
        firm_name, 
        firm_url, 
        extract_date 
    FROM Firms 
    ORDER BY extract_date DESC
    LIMIT %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_without_localisation(conn):
    """
    Lister les firmes sans localisation.
    """
    query = """
    SELECT 
        firm_name, 
        firm_url, 
        mail 
    FROM Firms 
    WHERE localisation IS NULL OR localisation = '{}';
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_with_few_reviews_but_high_rating(conn, max_reviews, min_rating):
    """
    Lister les firmes ayant reçu peu d'avis mais une excellente note.
    """
    query = """
    SELECT 
        firm_name, 
        nb_review, 
        note 
    FROM Firms 
    WHERE nb_review < %s AND note > %s
    ORDER BY note DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query, (max_reviews, min_rating))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_with_most_subcategories(conn):
    """
    Trouver les firmes ayant le plus grand nombre de sous-catégories.
    """
    query = """
    SELECT 
        f.firm_name, 
        COUNT(fc.subcategory_name) AS subcategory_count 
    FROM Firms f
    JOIN Firm_Subcategories fc ON f.firm_id = fc.firm_id
    GROUP BY f.firm_name
    ORDER BY subcategory_count DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_most_popular_subcategories(conn):
    """
    Lister les sous-catégories les plus populaires par nombre de firmes.
    """
    query = """
    SELECT 
        fc.subcategory_name, 
        COUNT(f.firm_id) AS firm_count 
    FROM Firm_Subcategories fc
    JOIN Firms f ON fc.firm_id = f.firm_id
    GROUP BY fc.subcategory_name
    ORDER BY firm_count DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_firms_with_majority_five_stars(conn):
    """
    Récupérer les firmes où plus de 50% des avis sont de 5 étoiles.
    """
    query = """
    SELECT 
        f.firm_name, 
        f.nb_review, 
        fs.percentage 
    FROM Firms f
    JOIN Firm_Star_Percs fs ON f.firm_id = fs.firm_id
    WHERE fs.star_value = 5 AND fs.percentage > 50
    ORDER BY fs.percentage DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_verified_firms_with_min_reviews(conn, min_reviews):
    """
    Récupérer les firmes vérifiées avec un nombre d'avis supérieur à un seuil.
    """
    query = """
    SELECT 
        firm_name, 
        nb_review, 
        note 
    FROM Firms 
    WHERE verified = TRUE AND nb_review > %s
    ORDER BY nb_review DESC;
    """
    cursor = conn.cursor()
    cursor.execute(query, (min_reviews,))
    results = cursor.fetchall()
    cursor.close()
    return results

# Fonction pour écrire les résultats dans un fichier texte
def write_to_file(filename, data):
    """Écrit les résultats dans un fichier texte."""
    with open(filename, 'a') as f:  # 'a' pour ajouter à la fin du fichier
        f.write(data + '\n')  # Ajouter une nouvelle ligne après chaque écriture

# Fonction principale pour exécuter les requêtes
def main():
    conn = psycopg2.connect(
        database="dst_db",
        user="daniel",
        password="datascientest",
        host="pg_container",
        port="5432"
        #connect_timeout=10  # Timeout après 10 secondes si la connexion échoue
    )
    time.sleep(30)
    # Créer les tables si elles n'existent pas
    create_tables(conn)
    
    # Test pour vérifier si les tables sont bien créées
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print("Tables disponibles dans la base de données:", tables)
    
    # Compter le nombre de firmes par sous-catégorie
    firms_per_subcategory = count_firms_per_subcategory(conn)
    print("\nNombre de firmes par sous-catégorie:", firms_per_subcategory)
    write_to_file('./psgr/output.txt', "\nNombre de firmes par sous-catégorie:")
    for subcategory, count in firms_per_subcategory:
        write_to_file('output.txt', f"{subcategory}: {count}")

    # Obtenir les firmes ayant une note supérieure à un certain seuil
    high_rating_firms = get_firms_with_high_ratings(conn, 4.0)
    print("\nFirmes avec une note supérieure à 4.0:", high_rating_firms)
    write_to_file('./psgr/output.txt', "\nFirmes avec une note supérieure à 4.0:")
    for firm_name, note, nb_review in high_rating_firms:
        write_to_file('./psgr/output.txt', f"{firm_name}: {note} ({nb_review} avis)")

    # Obtenir les firmes avec un nombre d'avis dans une certaine plage
    firms_in_review_range = get_firms_by_review_count_range(conn, 50, 200)
    print("\nFirmes avec un nombre d'avis entre 50 et 200:", firms_in_review_range) 
    write_to_file('./psgr/output.txt', "\nFirmes avec un nombre d'avis entre 50 et 200:")
    for firm_name, nb_review, note in firms_in_review_range:
        write_to_file('./psgr/output.txt', f"{firm_name}: {nb_review} avis ({note})")

        # Récupérer les firmes vérifiées avec un certain nombre d'avis
    verified_firms = get_verified_firms_with_min_reviews(conn, 100)
    print("\nFirmes vérifiées avec plus de 100 avis:", verified_firms)

    # Trouver les firmes avec une majorité de 5 étoiles
    firms_majority_five_stars = get_firms_with_majority_five_stars(conn)
    print("\nFirmes avec une majorité de 5 étoiles:", firms_majority_five_stars)

    # Sous-catégories les plus populaires
    popular_subcategories = get_most_popular_subcategories(conn)
    print("\nSous-catégories les plus populaires:", popular_subcategories)

    # Firmes avec le plus de sous-catégories
    firms_most_subcategories = get_firms_with_most_subcategories(conn)
    print("\nFirmes avec le plus de sous-catégories:", firms_most_subcategories)

    # Firmes avec peu d'avis mais une excellente note
    few_reviews_high_rating = get_firms_with_few_reviews_but_high_rating(conn, 50, 4.5)
    print("\nFirmes avec peu d'avis mais une excellente note:", few_reviews_high_rating)

    # Firmes extraites récemment
    recent_firms = get_most_recent_firms(conn, 10)
    print("\nLes 10 firmes extraites récemment:", recent_firms)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
