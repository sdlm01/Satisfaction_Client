#!/bin/sh

# script review
#python3 crawl/crawl_src/exe_update_review.py &
docker run --rm --network project_my_network_from_compose --entrypoint python project_crawl exe_update_review.py 
# script firm
#python3 crawl/crawl_src/exe_update_firmInfos.py &

#python3 crawl/crawl_src/main.py
#echo "Cron Job" 
