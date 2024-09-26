print("Crawl Container")
print("""
    Crawl Container
    ---------------------------------------------------------------------------------------
    EntryPoint: exe_update_review.py
        Recupere toutes les nouvelles reviews des firms presentes dans conf/firms.properties   
        Cree un fichier csv dans out/ : today(%Y-%m-%d)_update_reviews
    EntryPoint: exe_update_firmInfo.py: 
        Recupere toutes les nouvelles infos des firms presentes dans conf/firms.properties   
        Cree un fichier json dans out/ : today(%Y-%m-%d)_update_firms_infos
    """)