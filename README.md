# nb_cron
[![Install with conda](https://anaconda.org/alexanghh/nb_cron/badges/installer/conda.svg
)](https://anaconda.org/alexanghh/nb_cron)
[![PyPI version](https://badge.fury.io/py/nb-cron.svg)](https://pypi.org/project/nb-cron/)
[![Build Status](https://travis-ci.com/alexanghh/nb_cron.svg)](https://travis-ci.com/github/alexanghh/nb_cron) 
[![Coverage Status](https://coveralls.io/repos/github/alexanghh/nb_cron/badge.svg?branch=master)](https://coveralls.io/github/alexanghh/nb_cron?branch=master)

Provides crontab access from within Jupyter.

## Cron tab in the Jupyter file browser

This extension adds a *Cron* tab to the Jupyter file browser. Features include:

* View the list of the cron job(s) that currently exist.
  * Edit existing cron job(s)
  * Delete existing cron job(s)
* Add new cron job

## Installation
After installing the package using conda or pip, you can add nb_cron to jupyter as follows:
```
jupyter nbextension install nb_cron --py --sys-prefix --symlink
jupyter nbextension enable nb_cron --py --sys-prefix
jupyter serverextension enable nb_cron --py --sys-prefix
```

### Managing Cron Jobs

To create a new cron job:
* Use the *Create New Cron Job* button at the top of the page, and fill in the bash command and cron schedule.

To edit an existing cron job:
* Click the *Edit* button on the left of a cron job listing and fill in the bash command and cron schedule.

To delete an existing cron job:
* Click the *Trash* button on the left of a cron job listing to delete the cron job.