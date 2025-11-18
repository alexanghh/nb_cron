#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
import sys
import subprocess

import requests
from traitlets.config.loader import Config

import nb_cron


def url_path_join(*pieces):
    """Join components of url into a relative url.
    Use public API instead of internal routing methods.
    """
    return "/".join(s.strip("/") for s in pieces)


class NbCronAPI(object):
    """Wrapper for nbconvert API calls."""

    def __init__(self, base_url, token):
        self.base_url = str(base_url)
        self.token = str(token)

    def _req(self, verb, path, body=None, params=None):
        if body is None:
            body = {}

        session = requests.session()
        resp = session.get(self.base_url + '?token=' + self.token, allow_redirects=True)
        xsrf_token = None
        if '_xsrf' in session.cookies:
            xsrf_token = session.cookies['_xsrf']
        body.update({'_xsrf': xsrf_token})
        response = session.request(
            verb,
            url_path_join(self.base_url, 'cron', *path),
            data=body, params=params,
        )
        return response

    def get(self, path, body=None, params=None):
        return self._req('GET', path, body, params)

    def post(self, path, body=None, params=None):
        return self._req('POST', path, body, params)

    def jobs(self):
        res = self.get(["jobs"])
        if res is not None:
            return res.json()
        else:
            return {}


async def test_jp_fetch(jp_fetch):
    r = await jp_fetch("api", "spec.yaml")
    assert r.code == 200
