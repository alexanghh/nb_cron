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

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from traitlets.config.loader import Config

import nb_cron


@pytest.fixture
def driver(jp_serverapp):
    options = Options()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()


def test_01_body(driver, jp_serverapp):
    body = None
    try:
        url = f"http://localhost:{jp_serverapp.port}{jp_serverapp.base_url}?token={jp_serverapp.token}"
        driver.get(url)
        driver.implicitly_wait(30)  # seconds
        body = driver.find_element(By.TAG_NAME,"body")
    except NoSuchElementException:
        pass
    assert body is not None


def test_02_cron_tab(driver, jp_serverapp):
    cron_tab = None
    try:
        url = f"http://localhost:{jp_serverapp.port}{jp_serverapp.base_url}?token={jp_serverapp.token}"
        driver.get(url)
        driver.implicitly_wait(30)  # seconds
        cron_tab = driver.find_element(By.ID, "cron_tab")
    except NoSuchElementException:
        pass
    assert cron_tab is not None


def test_03_job_list(driver, jp_serverapp):
    job_list = None
    try:
        url = f"http://localhost:{jp_serverapp.port}{jp_serverapp.base_url}?token={jp_serverapp.token}"
        driver.get(url)
        driver.implicitly_wait(30)  # seconds
        job_list = driver.find_element(By.ID, "job_list_body")
    except NoSuchElementException:
        pass
    assert job_list is not None


def test_04_create_job(driver, jp_serverapp):
    job_list = None
    try:
        url = f"http://localhost:{jp_serverapp.port}{jp_serverapp.base_url}?token={jp_serverapp.token}"
        driver.get(url)
        driver.implicitly_wait(30)  # seconds
        job_list = driver.find_element(By.ID, "job_list_body")
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "cron_tab"))).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "new_job"))).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "job_schedule"))).send_keys("* * * * *")
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "check_schedule"))).click()
    except NoSuchElementException:
        pass
    assert job_list is not None


def test_05_papermill_builder(driver, jp_serverapp):
    job_list = None
    try:
        url = f"http://localhost:{jp_serverapp.port}{jp_serverapp.base_url}?token={jp_serverapp.token}"
        driver.get(url)
        driver.implicitly_wait(30)  # seconds
        job_list = driver.find_element(By.ID, "job_list_body")
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "cron_tab"))).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "new_job"))).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "papermill_builder"))).click()
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "notebook_input"))).send_keys("tests/pyspark parameter test.ipynb")
        WebDriverWait(driver, 30).until(expected_conditions.element_to_be_clickable((By.ID, "inspect_notebook"))).click()
    except NoSuchElementException:
        pass
    assert job_list is not None
