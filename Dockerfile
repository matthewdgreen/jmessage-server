FROM tiangolo/uwsgi-nginx-flask:flask-index

MAINTAINER J. Ayo Akinyele <jakinye3@jhu.edu> 

RUN echo "deb http://ftp.de.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends vsftpd
RUN apt-get install -y openjdk-8-jdk
RUN apt-get clean

RUN pip install psycopg2 flask-sqlalchemy

ADD vsftpd.conf /etc/vsftpd.conf

# ftp setup
RUN mkdir -p /ftp
RUN mkdir -p /var/run/vsftpd/empty

# for the database
RUN mkdir -p /data

RUN echo "\n[program:vsftpd]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "command=/usr/sbin/vsftpd" >> /etc/supervisor/conf.d/supervisord.conf

#VOLUME ["/ftp"]

EXPOSE 20 21
EXPOSE 12020 12021 12022 12023 12024 12025

COPY ./app /app

RUN python /app/init_db.py

RUN echo "\n[program:start_alice]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "command=/app/start_alice.sh" >> /etc/supervisor/conf.d/supervisord.conf

RUN echo "\n[program:start_bob]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "command=/app/start_bob.sh" >> /etc/supervisor/conf.d/supervisord.conf
