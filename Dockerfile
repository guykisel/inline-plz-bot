FROM tiangolo/uwsgi-nginx-flask:flask

RUN apt-get update && apt-get install -y \
	curl git bzr mercurial build-essential \
	zip ruby-full haskell-platform shellcheck \
	python-pip python-dev \
	nodejs build-essential 

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION node

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default \
    && npm install -g jsonlint jscs eslint jshint

ENV NODE_PATH $NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN echo '. "$NVM_DIR/nvm.sh"' >> /etc/profile
RUN echo NODE_VERSION=$NODE_VERSION >> /etc/environment
RUN echo NVM_DIR=$NVM_DIR >> /etc/environment
RUN echo NODE_PATH=$NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules >> /etc/environment
RUN echo PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH >> /etc/environment

RUN pip install -U pip

COPY ./app /app
COPY requirements.txt /app

RUN pip install -r /app/requirements.txt
