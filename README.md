# Satisfaction_Client
# CRAWLER

2024-08-10: S. NAVARRO

Extraction des infos firm pour une categorie:
    exe_categorie_get_all_firms_infos.py
    Parametre à modifier sur le script:
        USE_DELAY = True / False
        CATEGORIE = exemple: "atm"

Extraction des reviews d'une firme:
    exe_firm_get_all_reviews.py
    Parametre a modifier sur le script:
        USE_DELAY = True / False
        FIRM: firme to crawl, ex: priveeshop.com, turbodebt.com

Parametres communs: modifier les parametres dans common.py
    OUTPUT_FOLDER = "C://tmp//out//"
    TEMP_FOLDER = "C://tmp//"
    DELAY_PER_PAGE_SECONDS = 3
    DELAY_TIME = 120
    # verifier utilisation
    JSON_OUTPUT= True
    CSV_OUTPUT= False

Organisation des scripts
    common.py: contient toutes les fonctions utilitaires.
        getPageSoup: request truspilot et retry les 403 apres un delai
        getLastPage: retourne le int de la derniere page presente sur une page
        fileAggregation: aggregation de fichiers generique
    exe_: scripts executables
        gere les actions sur le systeme (creation de dossier ou autre)
        contient les principaux parametres (categorie, firm).
        script lancé via unix
    categorie_*, firm_*: script pagiination et crawl Bs
        gere le parcours des pages
        utilisent une fonction *_onePage_* contenant le mapping Bs
    manual_*: not finish yet
        test du parametrage via unix
        todo: version win

