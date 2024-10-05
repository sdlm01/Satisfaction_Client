print("Crawl Container")
print("""
    Crawl Container
    ---------------------------------------------------------------------------------------
    EntryPoint: exe_update_review.py:
        PURPOSE: a partir de la liste des firms presentes sur mongoDb
            Load toutes les nouvelles reviews et update les firmInfos dans mongoDB
        Execution: 
        docker run --rm --network project_my_network_from_compose --entrypoint python project_crawl exe_update_review.py 
    """)