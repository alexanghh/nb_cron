#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
# pylint: disable=W0221

# Tornado get and post handlers often have different args from their base class
# methods.

import json
import os
import re

from subprocess import Popen
from tempfile import TemporaryFile

from pkg_resources import parse_version
from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import APIHandler
from tornado import web

from .jobmanager import JobManager

static = os.path.join(os.path.dirname(__file__), 'static')

NS = r'cron'


class JobBaseHandler(APIHandler):
    """
    Mixin for a job manager. Just maintains a reference to the
    'job_manager' which implements all of the cron functions.
    """

    @property
    def job_manager(self):
        """Return our job_manager instance"""
        return self.settings['job_manager']


class MainJobHandler(JobBaseHandler):
    """
    Handler for `GET /jobs` which lists the jobs.
    """

    @web.authenticated
    def get(self):
        self.finish(json.dumps(self.job_manager.list_jobs()))


class JobActionHandler(JobBaseHandler):
    """
    Handler for `POST /jobs/<job>/{delete,edit,create}`
    which performs the requested action on the cron job.
    """

    @web.authenticated
    def post(self, job, action):
        status = None

        if action == 'remove':
            data = self.job_manager.remove_job(int(job))
        elif action == 'edit':
            schedule = self.get_argument('schedule', default=None)
            command = self.get_argument('command', default=None)
            comment = self.get_argument('comment', default=None)
            if not schedule or not command:
                raise web.HTTPError(
                    status_code=422,
                    reason=u"Schedule/Command empty.",
                )
            data = self.job_manager.edit_job(int(job), schedule, command, comment)
        elif action == 'create':
            schedule = self.get_argument('schedule', default=None)
            command = self.get_argument('command', default=None)
            comment = self.get_argument('comment', default=None)
            if not schedule or not command:
                raise web.HTTPError(
                    status_code=422,
                    reason=u"Schedule/Command is empty.",
                )
            data = self.job_manager.create_job(schedule, command, comment)
            if 'error' not in data:
                status = 201  # CREATED

        # catch-all ok
        if 'error' in data:
            raise web.HTTPError(
                status_code=data['status_code'] or 400,
                reason=data['message'],
            )

        self.set_status(status or 200)
        self.finish(json.dumps(data))

class ScheduleActionHandler(JobBaseHandler):
    """
    Handler for `POST /schedule/{check}`
    which performs the requested action on the cron schedule.
    """

    @web.authenticated
    def post(self, action):
        if action == 'check':
            schedule = self.get_argument('schedule', default=None)
            if not schedule:
                raise web.HTTPError(
                    status_code=422,
                    reason=u"Schedule empty",
                )
            data = self.job_manager.check_schedule(schedule)

        # catch-all ok
        if 'error' in data:
            raise web.HTTPError(
                status_code=data['status_code'] or 400,
                reason=data['message'],
            )

        self.finish(json.dumps(data))

class NotebookActionHandler(JobBaseHandler):
    """
    Handler for `POST /notebook/{papermill}`
    which performs the requested action on the cron schedule.
    """

    @web.authenticated
    def post(self, action):
        if action == 'papermill':
            path = self.get_argument('path', default=None)
            if not path:
                raise web.HTTPError(
                    status_code=422,
                    reason=u"Path empty",
                )
            data = self.job_manager.extract_papermill_parameters(path)

        # catch-all ok
        if 'error' in data:
            raise web.HTTPError(
                status_code=data['status_code'] or 400,
                reason=data['message'],
            )

        self.finish(json.dumps(data))

# -----------------------------------------------------------------------------
# URL to handler mappings
# -----------------------------------------------------------------------------

_job_action_regex = r"(?P<action>create|edit|remove)"
_schedule_action_regex = r"(?P<action>check)"
_notebook_action_regex = r"(?P<action>papermill)"

# there is almost no text that is invalid, but no hyphens up front, please
# neither all these suspicious but valid characters...
_job_regex = r"(?P<job>-1|\d+)"

default_handlers = [
    (r"/jobs", MainJobHandler),
    (r"/jobs/%s/%s" % (_job_regex, _job_action_regex),
     JobActionHandler),
    (r"/schedule/%s" % (_schedule_action_regex),
     ScheduleActionHandler),
    (r"/notebook/%s" % (    _notebook_action_regex),
     NotebookActionHandler),
]


def load_jupyter_server_extension(nbapp):
    """Load the nbserver extension"""
    webapp = nbapp.web_app
    webapp.settings['job_manager'] = JobManager(parent=nbapp)

    base_url = webapp.settings['base_url']
    webapp.add_handlers(".*$", [
        (ujoin(base_url, NS, pat), handler)
        for pat, handler in default_handlers
    ])
    nbapp.log.info("[nb_cron] enabled")
