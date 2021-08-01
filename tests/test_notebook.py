#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
import sys

from notebook.nbextensions import enable_nbextension_python, install_nbextension_python
from notebook.serverextensions import toggle_serverextension_python
from notebook.tests.launchnotebook import NotebookTestBase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from traitlets.config.loader import Config

import nb_cron


class NbCronNotebookTest(NotebookTestBase):
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
        super(NbCronNotebookTest, self).setUp()
        self.__class__.notebook.init_server_extension_config()
        self.__class__.notebook.init_server_extensions()

        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)

    def tearDown(self):
        self.driver.quit()
        super(NbCronNotebookTest, self).tearDown()

    def test_01_body(self):
        body = None
        try:
            self.driver.get(self.base_url() + '?token=' + self.token)
            self.driver.implicitly_wait(30)  # seconds
            body = self.driver.find_element_by_tag_name("body")
        except NoSuchElementException:
            pass
        self.assertIsNotNone(body)

    def test_02_cron_tab(self):
        cron_tab = None
        try:
            self.driver.get(self.base_url() + '?token=' + self.token)
            self.driver.implicitly_wait(30)  # seconds
            cron_tab = self.driver.find_element_by_id("cron_tab")
        except NoSuchElementException:
            pass
        self.assertIsNotNone(cron_tab)

    def test_03_job_list(self):
        job_list = None
        try:
            self.driver.get(self.base_url() + '?token=' + self.token)
            self.driver.implicitly_wait(30)  # seconds
            job_list = self.driver.find_element_by_id("job_list_body")
        except NoSuchElementException:
            pass
        self.assertIsNotNone(job_list)

    def test_04_create_job(self):
        job_list = None
        try:
            self.driver.get(self.base_url() + '?token=' + self.token)
            self.driver.implicitly_wait(30)  # seconds
            job_list = self.driver.find_element_by_id("job_list_body")
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "cron_tab"))).click()
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "new_job"))).click()
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "job_schedule"))).send_keys("* * * * *")
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "check_schedule"))).click()
        except NoSuchElementException:
            pass
        self.assertIsNotNone(job_list)

    def test_05_papermill_builder(self):
        job_list = None
        try:
            self.driver.get(self.base_url() + '?token=' + self.token)
            self.driver.implicitly_wait(30)  # seconds
            job_list = self.driver.find_element_by_id("job_list_body")
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "cron_tab"))).click()
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "new_job"))).click()
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "papermill_builder"))).click()
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "notebook_input"))).send_keys("tests/pyspark parameter test.ipynb")
            WebDriverWait(self.driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "inspect_notebook"))).click()
        except NoSuchElementException:
            pass
        self.assertIsNotNone(job_list)
