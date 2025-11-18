#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
import sys
import subprocess
import pytest

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

    def __init__(self, jp_serverapp):
        self.jp_serverapp = jp_serverapp

    @property
    def base_url(self):
        return f"http://localhost:{self.jp_serverapp.port}{self.jp_serverapp.base_url}"

    @property
    def token(self):
        return self.jp_serverapp.token

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


@pytest.fixture
def cron_api(jp_serverapp):
    print("Creating NbCronAPI")
    api = NbCronAPI(jp_serverapp)
    print("NbCronAPI created")
    return api


@pytest.fixture
def job(cron_api):
    job_schedule = "* * * * *"
    job_command = "echo"
    job_comment = "comment"
    cron_api.post(["jobs", str(-1), "create"], params={"schedule": job_schedule, "command": job_command, "comment": job_comment})
    jobs = cron_api.jobs()["jobs"]
    job_id = jobs[-1]["id"]
    yield
    cron_api.post(["jobs", str(job_id), "remove"])


def test_01_job_list(cron_api, job):
    jobs = cron_api.jobs()
    root = filter(lambda job: job["schedule"] == "* * * * *",
                  jobs["jobs"])
    assert len(list(root)) >= 1


def test_02_job_create_and_remove(cron_api):
    job_schedule = "* * * * *"
    job_command = "echo"
    job_comment = "comment"
    r = cron_api.post(["jobs", str(-1), "create"], params={"schedule": job_schedule, "command": job_command, "comment": job_comment})
    assert r.status_code == 201
    jobs = cron_api.jobs()["jobs"]
    job_id = jobs[-1]["id"]
    r = cron_api.post(["jobs", str(job_id), "remove"])
    assert r.status_code == 200


def test_03_job_create_fail(cron_api):
    r = cron_api.post(["jobs", str(-1), "create"], params={"schedule": " ", "command": "echo", "comment": "comment"})
    assert r.status_code == 422
    r = cron_api.post(["jobs", str(-1), "create"], params={"schedule": "* * * * * *", "command": "echo", "comment": "comment"})
    assert r.status_code == 422


def test_04_job_remove_fail(cron_api):
    r = cron_api.post(["jobs", ' ', "remove"])
    assert r.status_code == 404
    r = cron_api.post(["jobs", str(-2), "remove"])
    assert r.status_code == 404
    r = cron_api.post(["jobs", str(999999), "remove"])
    assert r.status_code == 422


def test_05_job_create_edit_remove(cron_api):
    job_schedule = "* * * * *"
    job_command = "echo"
    job_comment = "comment"
    r = cron_api.post(["jobs", str(-1), "create"], params={"schedule": job_schedule, "command": job_command, "comment": job_comment})
    assert r.status_code == 201
    jobs = cron_api.jobs()["jobs"]
    job_id = jobs[-1]["id"]
    r = cron_api.post(["jobs", str(job_id), "edit"], params={"schedule": job_schedule, "command": "echo edit test", "comment": job_comment})
    assert r.status_code == 200
    r = cron_api.post(["jobs", str(job_id), "remove"])
    assert r.status_code == 200


def test_06_job_edit_fail(cron_api, job):
    jobs = cron_api.jobs()["jobs"]
    job_id = jobs[-1]["id"]
    r = cron_api.post(["jobs", ' ', "edit"], params={"schedule": "* * * * *", "command": "echo", "comment": "comment"})
    assert r.status_code == 404
    r = cron_api.post(["jobs", str(8888), "edit"], params={"schedule": "* * * * *", "command": "echo", "comment": "comment"})
    assert r.status_code == 422
    r = cron_api.post(["jobs", str(job_id), "edit"], params={"schedule": "* * * * *", "command": " ", "comment": "comment"})
    assert r.status_code == 422
    r = cron_api.post(["jobs", str(job_id), "edit"], params={"schedule": " ", "command": "echo", "comment": "comment"})
    assert r.status_code == 422
    r = cron_api.post(["jobs", str(job_id), "edit"], params={"schedule": "* * * * * *", "command": "echo", "comment": "comment"})
    assert r.status_code == 422


def test_07_job_nonsense(cron_api, job):
    jobs = cron_api.jobs()["jobs"]
    job_id = jobs[-1]["id"]
    r = cron_api.post(["jobs", str(job_id), "nonsense"])
    assert r.status_code == 404


def test_08_schedule_check(cron_api):
    r = cron_api.post(["schedule", "check"], params={"schedule": "* * * * *"})
    assert r.status_code == 200


def test_09_schedule_check_fail(cron_api):
    r = cron_api.post(["schedule", "check"], params={"schedule": " "})
    assert r.status_code == 422
    r = cron_api.post(["schedule", "check"], params={"schedule": "* * * * * *"})
    assert r.status_code == 422


def test_10_extract_papermill_parameters(cron_api):
    r = cron_api.post(["notebook", "papermill"], params={"path": "tests/python parameter test.ipynb"})
    assert r.status_code == 200
    r = cron_api.post(["notebook", "papermill"], params={"path": "tests/spark parameter test.ipynb"})
    assert r.status_code == 200
    r = cron_api.post(["notebook", "papermill"], params={"path": "tests/pyspark parameter test.ipynb"})
    assert r.status_code == 200


def test_11_extract_papermill_parameters_fail(cron_api):
    r = cron_api.post(["notebook", "papermill"], params={"path": " "})
    assert r.status_code == 422
    r = cron_api.post(["notebook", "papermill"], params={"path": "test.ipynb"})
    assert r.status_code == 422
