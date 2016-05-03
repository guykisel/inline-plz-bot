# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return 'https://github.com/guykisel/inline-plz-bot'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
