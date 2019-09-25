sudo docker build -t grogsocket .
sudo docker run --rm -it -p 9001:9001 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v $(readlink -f /etc/letsencrypt/live/www.capnflint.com/privkey.pem):certs/privkey.pem:ro -v $(readlink -f /etc/letsencrypt/live/www.capnflint.com/fullchain.pem):certs/fullchain.pem:ro -name grogsocket grogsocket