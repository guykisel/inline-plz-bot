FROM tiangolo/uwsgi-nginx-flask:flask

RUN apt-get update && apt-get upgrade --fix-missing -y
RUN apt-get update && apt-get install -y curl git bzr mercurial build-essential
RUN apt-get install -y zip ruby-full haskell-platform shellcheck
RUN apt-get install -y python-pip python-dev
RUN apt-get install -y nodejs build-essential golang

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
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
RUN export PATH="/root/.pyenv/bin:$PATH"
ENV PATH /root/.pyenv/bin:$PATH
RUN eval "$(pyenv init -)"
RUN eval "$(pyenv virtualenv-init -)"
RUN pyenv update
RUN pyenv install 2.7.13
RUN pyenv install 3.6.0
COPY ./app /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

# Install rvm (https://github.com/vallard/docker/blob/master/rails/Dockerfile)
RUN apt-get install -y curl patch gawk g++ gcc make libc6-dev patch libreadline6-dev zlib1g-dev libssl-dev libyaml-dev libsqlite3-dev sqlite3 autoconf libgdbm-dev libncurses5-dev automake libtool bison pkg-config libffi-dev
RUN useradd -ms /bin/bash app
USER app
RUN gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
RUN /bin/bash -l -c "curl -L get.rvm.io | bash -s stable --rails"
RUN /bin/bash -l -c "rvm install 2.1"
RUN /bin/bash -l -c "echo 'gem: --no-ri --no-rdoc' > ~/.gemrc"
RUN /bin/bash -l -c "gem install bundler --no-ri --no-rdoc"
