# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import subprocess
import tempfile
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return 'https://github.com/guykisel/inline-plz-bot'

    # https://developer.github.com/v3/activity/events/types/#pullrequestevent
    data = request.get_json()
    pull_request = data['pull_request']['number']
    repo_slug = data['repository']['full_name']
    token = os.environ.get('TOKEN')
    interface = 'github'
    url = os.environ.get('URL', 'https://github.com')
    zero_exit = True
    install = True

    branch = data['pull_request']['head']['ref']
    pull_request_slug = data['pull_request']['head']['repo']['full_name']
    clone_url = data['pull_request']['head']['repo']['full_name']['clone_url']

    # make temp dir
    tempdir = tempfile.mkdtemp()

    # git clone into temp dir

    # run inline-plz in temp dir

    # delete temp dir


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
