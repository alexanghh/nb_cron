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
            self.log.error('[nb_cron] Schedule check fail:\n%s', err)
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

    def check_variables(self, _nb_cron_code):
        try:
            # exec code to get variable names and values
            exec(_nb_cron_code)
            var = locals()
            var.pop("_nb_cron_code")  # remove method parameter
            var.pop("self")  # remove self
            return var
        except SyntaxError  as err:
            self.log.error('[nb_cron] Check papermill parameters fail:\n%s', err)
            return {}

    def extract_papermill(self, path):
        """process notebook to get papermill inputs"""

        kernel = ""
        variables = {}
        try:
            import os
            notebook_input = os.path.abspath(path)
            notebook_output = notebook_input.replace(".ipynb", "_output.ipynb")
            notebook_string = open(notebook_input).read()
            notebook = json.loads(notebook_string)
            # get kernel
            env = ""
            kernel = notebook["metadata"]["kernelspec"]["name"]
            # check for conda env
            self.log.error('[nb_cron] conda_prefix:\n%s', self.conda_prefix)
            if kernel.startswith(self.conda_prefix):
                env_kernel = kernel[len(self.conda_prefix):].split(self.conda_separator)
                env = env_kernel[0]
                kernel = self.conda_separator.join(env_kernel[1:])
                if env and kernel == 'py':
                    kernel = 'python3'
            # get parameters cell
            code = ""
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    if "metadata" in cell and "tags" in cell["metadata"] and "parameters" in cell["metadata"]["tags"]:
                        code = "".join(cell["source"])
            variables = self.check_variables(code)
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
            "env": env,
            "kernel": kernel,
            "parameters": variables,
            "status_code": 200
        }
