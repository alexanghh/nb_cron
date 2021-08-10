#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
import datetime
import json

from crontab import CronTab
from traitlets import Dict, Unicode
from traitlets.config.configurable import LoggingConfigurable


class JobManager(LoggingConfigurable):
    conda_prefix = Unicode(
        help="prefix to detect conda", allow_none=True, default_value='conda-env-.conda-'
    ).tag(config=True, env="NBCRON_CONDA_PREFIX")
    conda_separator = Unicode(
        help="separator between env and kernel name", allow_none=True, default_value='-'
    ).tag(config=True, env="NBCRON_CONDA_SEPARATOR")

    jobs = Dict()

    def list_jobs(self):
        """List all cron jobs"""
        cron = CronTab(user=True)
        jobs = []
        for i in range(len(cron)):
            jobs.append({
                'id': i,
                'schedule': str(cron[i].slices),
                'command': str(cron[i].command),
                'comment': str(cron[i].comment)
            })

        self.log.debug("jobs: %s" % str(jobs))

        return {
            "jobs": jobs,
            "status_code": 200
        }

    def remove_job(self, job):
        cron = CronTab(user=True)
        try:
            self.log.debug('deleting cron job id %s', job)
            cron.remove(cron[job])
            cron.write()
        except Exception as err:
            self.log.error('[nb_cron] Job delete fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }

        return {'status_code': 200}

    def create_job(self, schedule, command, comment):
        cron = CronTab(user=True)
        try:
            self.log.debug('creating cron job schedule:%s command:%s comment:%s',
                           schedule, command, comment)
            job = cron.new(command=command, comment=comment, pre_comment=True)
            job.setall(schedule)
            if not job.is_valid():
                return {
                    "error": True,
                    "message": u"Job is invalid.",
                    "status_code": 422
                }
            cron.write()
        except KeyError as err:
            self.log.error('[nb_cron] Job create fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }

        return {
            'id': len(cron) - 1,
            'status_code': 200
        }

    def edit_job(self, job, schedule, command, comment):
        cron = CronTab(user=True)

        # check if job id is within range
        if job < 0 or job > len(cron):
            return {
                "error": True,
                "message": u"Job id not found.",
                "status_code": 422
            }

        job = cron[job]
        try:
            self.log.debug('editing cron job id:%s schedule:%s command:%s comment:%s',
                           str(job), schedule, command, comment)
            job.set_command(command)
            job.set_comment(comment, pre_comment=True)
            job.setall(schedule)
            if not job.is_valid():
                return {
                    "error": True,
                    "message": u"Job is invalid.",
                    "status_code": 422
                }
            cron.write()
        except KeyError as err:
            self.log.error('[nb_cron] Job edit fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }

        return {'status_code': 200}

    def check_schedule(self, schedule):
        """List next 5 schedule"""
        cron = CronTab(user=True)
        job = cron.new(command='')
        try:
            job.setall(schedule)
        except KeyError as err:
            self.log.debug('[nb_cron] Schedule check fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }

        sch = job.schedule(date_from=datetime.datetime.now())
        schedules = []
        for i in range(5):
            schedules.append(str(sch.get_next()))

        return {
            "schedules": schedules,
            "status_code": 200
        }

    def extract_variables(self, _nb_cron_code, _nb_cron_kernel='python'):
        """Extract declared variables from cell

        Args:
            _nb_cron_code: cell code
            _nb_cron_kernel: kernel of code for preprocessing

        Returns:
            dict of variables' name and value
        """
        try:
            self.log.debug('kernel: %s, original cell: %s', _nb_cron_kernel, _nb_cron_code)
            # check each line of code
            _nb_cron_code_cleaned = []
            for _nb_cron_code_line in _nb_cron_code.split("\n"):
                _nb_cron_code_line = _nb_cron_code_line.strip()
                # remove magic line
                if not _nb_cron_code_line.startswith("%"):
                    # remove val from scala spark code to mimic python code
                    if _nb_cron_kernel.startswith("spark") and _nb_cron_code_line.startswith("val "):
                        _nb_cron_code_line = _nb_cron_code_line[len("val "):]
                        # handle boolean case difference
                        _nb_cron_code_line = _nb_cron_code_line.replace("true", "True")
                        _nb_cron_code_line = _nb_cron_code_line.replace("false", "False")
                    _nb_cron_code_cleaned.append(_nb_cron_code_line)
            _nb_cron_code = "\n".join(_nb_cron_code_cleaned)
            self.log.debug('kernel: %s, processed cell: %s', _nb_cron_kernel, _nb_cron_code)

            # exec code to get variable names and values
            exec(_nb_cron_code)
            var = locals()
            var.pop("_nb_cron_code")  # remove method parameter
            var.pop("_nb_cron_code_cleaned")  # remove method parameter
            var.pop("_nb_cron_code_line")  # remove method parameter
            var.pop("_nb_cron_kernel")  # remove method parameter
            var.pop("self")  # remove self

            return var
        except NameError as err:
            self.log.error('[nb_cron] papermill extract parameters fail:\n%s', err)
            return {}
        except SyntaxError as err:
            self.log.error('[nb_cron] papermill extract parameters fail:\n%s', err)
            return {}

    def extract_papermill_parameters(self, path):
        """Process notebook to get papermill inputs

        Args:
            path: path to notebook

        Returns:
            successful - maps of notebook input/output abs path, env, kernel, parameters and status_code
            error - error message and  status_code
        """
        kernel = ""
        variables = {}
        try:
            import os
            notebook_input = os.path.abspath(path)
            notebook_output = notebook_input.replace(".ipynb", "_output.ipynb")
            notebook_cwd = os.sep.join(notebook_input.split(os.sep)[:-1])
            notebook_string = open(notebook_input).read()
            notebook = json.loads(notebook_string)
            # get kernel
            env = ""
            conda_activate = ""
            kernel = notebook["metadata"]["kernelspec"]["name"]
            # check for conda env
            if kernel.startswith(self.conda_prefix):
                env_kernel = kernel[len(self.conda_prefix):].split(self.conda_separator)
                env = env_kernel[0]
                kernel = self.conda_separator.join(env_kernel[1:])
                if env and kernel == 'py':
                    kernel = 'python3'
            else:
                # get current activated environment
                if 'CONDA_DEFAULT_ENV' in os.environ:
                    env = os.environ['CONDA_DEFAULT_ENV']
            # use CONDA_EXE instead of CONDA_PREFIX (assumes activate co-exists with conda)
            if 'CONDA_EXE' in os.environ:
                conda_activate = 'activate'.join(os.environ['CONDA_EXE'].rsplit('conda', 1))
                # defaults to empty if activate not found
                if not os.path.isfile(conda_activate):
                    conda_activate = ""
            self.log.debug('conda_activate: %s', conda_activate)

            # get parameters cell
            code = ""
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    if "metadata" in cell and "tags" in cell["metadata"] and "parameters" in cell["metadata"]["tags"]:
                        code = "".join(cell["source"])
            variables = self.extract_variables(code, kernel)
        except FileNotFoundError as err:
            self.log.error('[nb_cron] Extract papermill parameters fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }
        except KeyError as err:
            self.log.error('[nb_cron] Extract papermill parameters fail:\n%s', err)
            return {
                "error": True,
                "message": u"{err}".format(err=err),
                "status_code": 422
            }

        return {
            "input": notebook_input,
            "output": notebook_output,
            "cwd": notebook_cwd,
            "env": env,
            "activate": conda_activate,
            "kernel": kernel,
            "parameters": variables,
            "status_code": 200
        }
