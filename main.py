#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import logging.handlers
import os
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
from capturer import CaptureOutput
from flask import Flask, request, redirect

app = Flask(__name__)

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
rh = logging.handlers.RotatingFileHandler(
    os.path.join(os.path.expanduser('~'),
                 'inline-plz-bot.log',
                 maxBytes=1024 * 1024,
                 backupCount=5)
)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(rh)
logger.addHandler(ch)

SAFE_ENV = os.environ.copy()
# wipe our token before passing our envvars into inline-plz
SAFE_ENV['TOKEN'] = ''
DOTFILES = 'dotfiles'
STOP_FILE_NAME = '.inlineplzstop'
REVIEWS_IN_PROGRESS = dict()


@app.errorhandler(Exception)
def all_exception_handler():
    """Catch, print, then ignore all errors."""
    traceback.print_exc()


def clone(url, dir, token, ref=None):
    # https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth
    url = url.replace('https://', 'https://{}@'.format(token))
    logger.info('Cloning: {}'.format(url))
    try:
        os.makedirs(dir)
    except OSError:
        pass
    try:
        subprocess.check_call(
            ['git', 'init'],
            cwd=dir, env=SAFE_ENV
        )

        pull_cmd = ['git', 'pull', url]
        if ref:
            pull_cmd.append(ref)
        subprocess.check_call(
            pull_cmd,
            cwd=dir, env=SAFE_ENV
        )
        return True
    except subprocess.CalledProcessError:
        return False


def clone_dotfiles(url, org, tempdir, token):
    # https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth
    clone_url = '/'.join([url, org, DOTFILES]) + '.git'
    logger.info('Cloning: {}'.format(clone_url))
    dotfile_path = os.path.join(tempdir, DOTFILES)
    return clone(clone_url, dotfile_path, token)


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
        ref = data['pull_request']['head']['ref']
        clone_url = data['pull_request']['head']['repo']['clone_url']
        org = data['repository']['owner']['login']
    except KeyError:
        logger.exception('Invalid pull request data.')
        return 'Invalid pull request data.'
    trusted = os.environ.get('TRUSTED', '').lower().strip() in ['true', 'yes', '1']

    logger.info('Starting inline-plz:')
    logger.info('Event: {}'.format(event_type))
    logger.info('PR: {}'.format(pull_request))
    logger.info('Repo slug: {}'.format(repo_slug))
    logger.info('Name: {}'.format(name))
    logger.info('SHA: {}'.format(sha))
    logger.info('Clone URL: {}'.format(clone_url))

    if event_type not in ['opened', 'synchronize']:
        return

    # make temp dirs
    tempdir = tempfile.mkdtemp()
    dotfile_dir = tempfile.mkdtemp()
    time.sleep(1)

    # check for existing runs against this PR
    pr_name = '{}-{}'.format(repo_slug, pull_request)
    REVIEWS_IN_PROGRESS.setdefault(pr_name, set())
    for dir in REVIEWS_IN_PROGRESS[pr_name]:
        stopfile_path = os.path.join(dir, STOP_FILE_NAME)
        try:
            open(stopfile_path, 'w').close()
        except (IOError, OSError):
            pass
    REVIEWS_IN_PROGRESS[pr_name].add(tempdir)

    try:
        # git clone into temp dir
        clone(clone_url, os.path.join(tempdir, name), token, ref)
        time.sleep(1)

        # git checkout our sha
        subprocess.check_call(
            ['git', 'checkout', sha],
            cwd=os.path.join(tempdir, name), env=SAFE_ENV
        )
        time.sleep(1)

        args = [
            'inline-plz',
            '--autorun',
            '--repo-slug={}'.format(repo_slug),
            '--pull-request={}'.format(pull_request),
            '--url={}'.format(url),
            '--token={}'.format(token),
            '--interface={}'.format(interface),
            '--zero-exit'
        ]
        if trusted:
            args.append('--trusted')
        if clone_dotfiles(url, org, dotfile_dir, token):
            args.append('--config-dir={}'.format(
                os.path.join(dotfile_dir, 'dotfiles')
            ))
        time.sleep(1)

        # run inline-plz in temp dir
        logger.info('Args: {}'.format(args))
        with CaptureOutput() as capturer:
            try:
                subprocess.check_call(args, cwd=os.path.join(tempdir, name), env=SAFE_ENV)
                for line in capturer.get_lines():
                    logger.info(line)
            except subprocess.CalledProcessError:
                for line in capturer.get_lines():
                    logger.error(line)
                raise
        time.sleep(1)
    finally:
        # delete temp dir
        time.sleep(1)
        shutil.rmtree(tempdir, ignore_errors=True)
        shutil.rmtree(dotfile_dir, ignore_errors=True)
        REVIEWS_IN_PROGRESS[pr_name].discard(tempdir)


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
