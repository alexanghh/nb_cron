# nb_cron
[![Install with conda](https://anaconda.org/alexanghh/nb_cron/badges/installer/conda.svg
)](https://anaconda.org/alexanghh/nb_cron)
[![Build Status](https://travis-ci.com/alexanghh/nb_cron.svg)](https://travis-ci.com/github/alexanghh/nb_cron) 
[![Coverage Status](https://coveralls.io/repos/github/alexanghh/nb_cron/badge.svg?branch=master)](https://coveralls.io/github/alexanghh/nb_cron?branch=master)

Provides cron tab access extension from within Jupyter.

## Cron tab in the Jupyter file browser

This extension adds a Cron tab to the Jupyter file browser. Selecting the Cron tab
will display:

* A list of the cron job that currently exist

### Managing Cron Jobs

To create a new cron job:
* Use the *Create New Cron Job* button at the top of the page, and fill in the bash command and cron schedule.

To edit an existing cron job:
* Click the *Edit* button on the left of a cron job listing and fill in the bash command and cron schedule.

To delete an existing cron job:
* Click the *Trash* button on the left of a cron job listing to delete the cron job.