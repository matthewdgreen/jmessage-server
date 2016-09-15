FROM tiangolo/uwsgi-nginx-flask:flask-index

MAINTAINER J. Ayo Akinyele <jakinye3@jhu.edu> 

RUN pip install flask-sqlalchemy

COPY ./app /app

RUN python /app/init_db.py
