FROM python:3.8

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install mysqlclient  
RUN pip install django-sslserver
Run pip install yfpy

COPY . /code/