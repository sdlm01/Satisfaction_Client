#!/bin/bash
#RUN chmod -R 777 /usr/src/app
#echo "Cron Job" >> ~/cront.txt


cd /usr/src/app/


#/usr/local/bin/docker-compose -f docker-compose.yml restart crawl
#docker wait crawl
#/usr/local/bin/docker-compose -f docker-compose.yml restart mongo
#docker wait mongo
#/usr/local/bin/docker-compose -f docker-compose.yml restart psgr
#docker wait psgr
#/usr/local/bin/docker-compose -f docker-compose.yml restart ml
#docker wait ml
docker restart crawl
docker wait crawl
docker restart mongo
docker wait mongo
docker restart psgr
docker wait psgr
docker restart ml


#0 3 * * * docker restart mongo
#0 4 * * * docker restart psgr
#0 5 * * * docker restart ml


