FROM tiangolo/uwsgi-nginx-flask:flask

RUN apt-get update && apt-get install -y ruby-full haskell-platform shellcheck nodejs build-essential 

RUN pip install -U pip

COPY ./app /app
COPY requirements.txt /app

RUN pip install -r /app/requirements.txt
