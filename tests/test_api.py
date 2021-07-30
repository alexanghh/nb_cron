#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
import sys

import requests
from notebook.nbextensions import enable_nbextension_python, install_nbextension_python
from notebook.serverextensions import toggle_serverextension_python
from notebook.tests.launchnotebook import NotebookTestBase
from notebook.utils import url_path_join
from traitlets.config.loader import Config

import nb_cron


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


class NbCronAPITest(NotebookTestBase):
    def setUp(self):
        if 'nb_cron' not in sys.modules:
            sys.modules['nb_cron'] = nb_cron
        c = Config()
        c.NotebookApp.nbserver_extensions = {}
        c.NotebookApp.nbserver_extensions.update({'nb_cron': True})
        c.NotebookApp.allow_origin = '*'
        c.NotebookApp.allow_credentials = True
        c.NotebookApp.disable_check_xsrf = True
        self.config = c
        install_nbextension_python("nb_cron", user=True)
        enable_nbextension_python("nb_cron")
        toggle_serverextension_python("nb_cron", True)
        super(NbCronAPITest, self).setUp()
        self.__class__.notebook.init_server_extension_config()
        self.__class__.notebook.init_server_extensions()

        # chrome_options = Options()
        # # chrome_options.add_argument("--headless")
        # self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver.get(self.base_url() + '?token=' + self.token)
        # self.driver.implicitly_wait(120)  # seconds
        # import time
        # time.sleep(60)

        self.cron_api = NbCronAPI(self.base_url(), self.token)
        self.job_schedule = "* * * * *"
        self.job_command = "echo"
        self.job_comment = "comment"
        self.notebook_path = "tests/python parameter test.ipynb"
        self.create_job()
        self.job_id = len(self.cron_api.jobs()) - 1

    def tearDown(self):
        # self.driver.quit()
        self.remove_job(self.job_id)
        super(NbCronAPITest, self).tearDown()

    def create_job(self, schedule=None, command=None, comment=None):
        return self.cron_api.post(["jobs", str(-1),
                                   "create"],
                                  params={"schedule": schedule or self.job_schedule,
                                          "command": command or self.job_command,
                                          "comment": comment or self.job_comment})

    def remove_job(self, jid=None):
        return self.cron_api.post(["jobs", str(jid or self.job_id),
                                   "remove"])

    def edit_job(self, jid=None, schedule=None, command=None, comment=None):
        return self.cron_api.post(["jobs", str(jid or self.job_id),
                                   "edit"],
                                  params={"schedule": schedule or self.job_schedule,
                                          "command": command or self.job_command,
                                          "comment": comment or self.job_comment})

    def check_schedule(self, schedule=None):
        return self.cron_api.post(["schedule", "check"],
                                  params={"schedule": schedule or self.job_schedule})

    def extract_papermill_parameters(self, notebook_path=None):
        return self.cron_api.post(["notebook", "papermill"],
                                  params={"path": notebook_path or self.notebook_path})

    def test_01_job_list(self):
        jobs = self.cron_api.jobs()
        root = filter(lambda job: job["schedule"] == "* * * * *",
                      jobs["jobs"])
        self.assertGreaterEqual(len(list(root)), 1)

    def test_02_job_create_and_remove(self):
        self.assertEqual(self.create_job().status_code, 201)
        jid = len(self.cron_api.jobs()) - 1
        self.assertEqual(self.remove_job(jid).status_code, 200)

    def test_03_job_create_fail(self):
        self.assertEqual(self.create_job(schedule=" ").status_code, 422)
        self.assertEqual(self.create_job(schedule="* * * * * *").status_code, 422)
    
    def test_04_job_remove_fail(self):
        self.assertEqual(self.remove_job(' ').status_code, 404)
        self.assertEqual(self.remove_job(-2).status_code, 404)
        self.assertEqual(self.remove_job(999999).status_code, 422)

    def test_05_job_create_edit_remove(self):
        self.assertEqual(self.create_job().status_code, 201)
        jid = len(self.cron_api.jobs()) - 1
        self.assertEqual(self.edit_job(jid, command='echo edit test').status_code, 200)
        self.assertEqual(self.remove_job(jid).status_code, 200)

    def test_06_job_edit_fail(self):
        self.assertEqual(self.edit_job(jid=" ").status_code, 404)
        self.assertEqual(self.edit_job(jid=8888).status_code, 422)
        self.assertEqual(self.edit_job(command=" ").status_code, 422)
        self.assertEqual(self.edit_job(schedule=" ").status_code, 422)
        self.assertEqual(self.edit_job(schedule="* * * * * *").status_code, 422)

    def test_07_job_nonsense(self):
        r = self.cron_api.post(["jobs", str(self.job_id), "nonsense"])
        self.assertEqual(r.status_code, 404)

    def test_08_schedule_check(self):
        self.assertEqual(self.check_schedule().status_code, 200)

    def test_09_schedule_check_fail(self):
        self.assertEqual(self.check_schedule(schedule=' ').status_code, 422)
        self.assertEqual(self.check_schedule(schedule='* * * * * *').status_code, 422)

    def test_10_extract_papermill_parameters(self):
        self.assertEqual(self.extract_papermill_parameters(notebook_path='tests/python parameter test.ipynb').status_code, 200)
        self.assertEqual(self.extract_papermill_parameters(notebook_path='tests/spark parameter test.ipynb').status_code, 200)
        self.assertEqual(self.extract_papermill_parameters(notebook_path='tests/pyspark parameter test.ipynb').status_code, 200)

    def test_11_extract_papermill_parameters_fail(self):
        self.assertEqual(self.extract_papermill_parameters(notebook_path=' ').status_code, 422)
        self.assertEqual(self.extract_papermill_parameters(notebook_path='test.ipynb').status_code, 422)
