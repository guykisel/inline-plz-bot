# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import shutil
import subprocess
import tempfile
import time
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
    name = data['repository']['name']
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
    time.sleep(1)

    # git clone into temp dir
    subprocess.check_output(
        ['git', 'clone', clone_url],
        cwd=tempdir
    ).strip().decode('utf-8', errors='replace')
    time.sleep(1)

    # run inline-plz in temp dir
    subprocess.check_output(
        [
            'inline-plz',
            '--autorun',
            '--repo-slug={}'.format(repo_slug),
            '--pull-request={}'.format(pull_request),
            '--url={}'.format(url),
            '--token={}'.format(token),
            '--interface={}'.format(interface),
            '--zero-exit'
        ],
        cwd=os.path.join(tempdir, name)
    ).strip().decode('utf-8', errors='replace')
    time.sleep(1)

    # delete temp dir
    shutil.rmtree(tempdir)
    time.sleep(1)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)