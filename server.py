#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
from flask import Flask, request, redirect

app = Flask(__name__)


def clone_dotfiles(url, org, tempdir):
    clone_url = '/'.join([url, org, 'dotfiles']) + '.git'
    print('Cloning: {}'.format(clone_url))
    try:
        subprocess.check_call(
            ['git', 'clone', clone_url],
            cwd=tempdir
        )
        return True
    except subprocess.CalledProcessError:
        return False


def lint(data):
    try:
        pull_request = data['pull_request']['number']
        repo_slug = data['repository']['full_name']
        name = data['repository']['name']
        token = os.environ.get('TOKEN')
        interface = 'github'
        url = os.environ.get('URL', 'https://github.com')
        event_type = data['action']
        sha = data['pull_request']['head']['sha']
        pull_request_slug = data['pull_request']['head']['repo']['full_name']
        clone_url = data['pull_request']['head']['repo']['clone_url']
        org = data['repository']['owner']['login']
    except KeyError:
        traceback.print_exc()
        return 'Invalid pull request data.'

    print('Starting inline-plz:')
    print('Event: {}'.format(event_type))
    print('PR: {}'.format(pull_request))
    print('Repo slug: {}'.format(repo_slug))
    print('Name: {}'.format(name))
    print('SHA: {}'.format(sha))
    print('Clone URL: {}'.format(clone_url))

    if event_type not in ['opened', 'synchronize']:
        return

    # make temp dirs
    tempdir = tempfile.mkdtemp()
    dotfile_dir = tempfile.mkdtemp()
    time.sleep(1)

    try:
        # git clone into temp dir
        subprocess.check_call(
            ['git', 'clone', clone_url],
            cwd=tempdir
        )
        time.sleep(1)

        # git checkout our sha
        subprocess.check_call(
            ['git', 'checkout', sha],
            cwd=os.path.join(tempdir, name)
        )
        time.sleep(1)

        args = [
            'inline-plz',
            '--autorun',
            '--repo-slug={}'.format(repo_slug),
            '--pull-request={}'.format(pull_request),
            # '--url={}'.format(url),
            '--token={}'.format(token),
            '--interface={}'.format(interface),
            '--zero-exit'
        ]

        if clone_dotfiles(url, org, dotfile_dir):
            args.append('--config-dir="{}"'.format(
                os.path.join(dotfile_dir, 'dotfiles')
            ))
        time.sleep(1)

        # run inline-plz in temp dir
        print('Args: {}'.format(args))
        subprocess.check_call(args, cwd=os.path.join(tempdir, name))
        time.sleep(1)
    finally:
        # delete temp dir
        time.sleep(1)
        shutil.rmtree(tempdir)
        shutil.rmtree(dotfile_dir)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return redirect('https://github.com/guykisel/inline-plz-bot', code=302)

    # https://developer.github.com/v3/activity/events/types/#pullrequestevent
    data = request.get_json()
    lint_thread = threading.Thread(target=lint, args=(data, ))
    lint_thread.start()
    return 'Success!'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
