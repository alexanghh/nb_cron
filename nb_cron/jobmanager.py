import datetime

from crontab import CronTab
from traitlets import Dict
from traitlets.config.configurable import LoggingConfigurable


class JobManager(LoggingConfigurable):
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
