FROM tiangolo/uwsgi-nginx-flask:flask

COPY * /app

RUN apt-get update && apt-get install -y ruby-full haskell-platform shellcheck

RUN pip install -r /app/requirements.txt
