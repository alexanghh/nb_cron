# nb_cron

[![Anaconda version](https://anaconda.org/conda-forge/nb_cron/badges/version.svg)](https://anaconda.org/conda-forge/nb_cron)
[![Install with conda](https://anaconda.org/conda-forge/nb_cron/badges/installer/conda.svg)](https://anaconda.org/conda-forge/nb_cron)
[![PyPI version](https://badge.fury.io/py/nb-cron.svg)](https://pypi.org/project/nb-cron/)
[![Build Status](https://travis-ci.com/alexanghh/nb_cron.svg)](https://travis-ci.com/github/alexanghh/nb_cron) 
[![Coverage Status](https://coveralls.io/repos/github/alexanghh/nb_cron/badge.svg?branch=master)](https://coveralls.io/github/alexanghh/nb_cron?branch=master)

Provides crontab access from within Jupyter.

## Cron tab in the Jupyter file browser

This extension adds a *Cron* tab to the Jupyter file browser and a *Cron* menu item in notebook view. Features include:

* View the list of the cron job(s) that currently exist.
  * Edit existing cron job(s)
  * Delete existing cron job(s)
* Add new cron job
* Helper to build papermill command
  * Allows setting of notebook's environment, kernel and parameters
  * Able to inspect notebook (relative or full path) to extract environment, kernel and parameters to build papermill command and options

## Installation
After installing the package using conda or pip, you can add nb_cron to jupyter as follows:
```
jupyter nbextension install nb_cron --py --sys-prefix --symlink
jupyter nbextension enable nb_cron --py --sys-prefix
jupyter serverextension enable nb_cron --py --sys-prefix
```

### Cron tab in tree view

To create a new cron job:
* Use the *Create New Cron Job* button at the top of the page, and fill in the bash command and cron schedule.
* Use the *Notebook Command Builder* to build a bash command for running a notebook using papermill. 

To edit an existing cron job:
* Click the *Edit* button on the left of a cron job listing and fill in the bash command and cron schedule.

To delete an existing cron job:
* Click the *Trash* button on the left of a cron job listing to delete the cron job.

### Cron menu item in notebook view
To manage cron jobs
* Click *View cron jobs* (refer to cron tab in tree view)

To schedule new cron job for current notebook
* Click *Schedule notebook job*.
* Opens up the *Create new job* and *Notebook command builder* dialog. 
* Auto inspect notebook and fill up the *Notebook command builder* dialog.

To edit existing cron job that uses current notebook
* Click *Edit notebook job*.
* Only available if there is an existing cron job contains the current notebook in the cron command.
* Only able to edit the first job. Please use *View cron jobs* to edit if there are multiple jobs for the notebook.
