/*
 * Copyright (c) 2021, nb_cron Contributors
 *
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file LICENSE, distributed with this software.
 */
define([
    'jquery',
    'base/js/utils',
    './common',
    './urls',
], function ($, utils, common, urls) {
    "use strict";

    // define default values for config parameters
    var config = {
        papermill_path: 'papermill'
    };

    var NullView = {
        refresh: function () {
        }
    };

    var jobs = {
        all: [],
        view: NullView,

        load: function () {
            // Load the list via ajax to the /jobs endpoint
            var that = this;
            var error_callback = common.MakeErrorCallback('Error', 'An error occurred while listing cron jobs.');

            function handle_response(data, status, xhr) {
                var jobs = data.jobs || [];

                that.all = jobs;
                that.view.refresh(jobs);
            }

            var settings = common.AjaxSettings({
                success: common.SuccessWrapper(handle_response, error_callback),
                error: error_callback
            });

            return utils.ajax(urls.api_url + 'jobs', settings);
        },

        create: function (schedule, command, comment) {
            var error_callback = common.MakeErrorCallback('Error Creating Job', 'An error occurred while creating job "' +
                command + '"');

            function create_success() {
                // Refresh list of job since there is a new one
                jobs.load();
            }

            return cron_job_action({id: -1}, 'create', create_success, error_callback, {
                schedule: schedule,
                command: command,
                comment: comment
            });
        },

        edit: function (job, schedule, command, comment) {
            var error_callback = common.MakeErrorCallback('Error Editing Job', 'An error occurred while editing job "' + job.id + '"');

            function edit_success() {
                // Refresh list of jobs since there is a new one
                jobs.load();
            }

            return cron_job_action(job, 'edit', edit_success, error_callback, {
                schedule: schedule,
                command: command,
                comment: comment
            });
        },

        remove: function (job) {
            var error_callback = common.MakeErrorCallback('Error Removing Job', 'An error occurred while removing job "' + job.id + '"');

            function remove_success() {
                // Refresh list of jobs since there is a new one
                jobs.load();
            }

            return cron_job_action(job, 'remove', remove_success, error_callback);
        }
    };

    function cron_job_action(job, action, on_success, on_error, data) {
        // Helper function to access the /jobs/JOB/ACTION endpoint

        var settings = common.AjaxSettings({
            data: data || {},
            type: 'POST',
            success: common.SuccessWrapper(on_success, on_error),
            error: on_error
        });

        var url = urls.api_url + utils.url_join_encode(
            'jobs', job.id, action);
        return utils.ajax(url, settings);
    }


    var schedule = {
        check: function (schedule, view) {
            var error_callback = common.MakeErrorCallback('Error Checking Schedule', 'An error occurred while checking schedule "' + schedule + '"');

            function show_schedule(data, status, xhr) {
                var schedules = data.schedules || [];
                view.html("<b>Sample Schedules:</b>")
                for (let i = 0; i < schedules.length; i++) {
                    view.append($('<div/>')
                        .addClass('list_item')
                        .addClass('row')
                        .text(schedules[i]))
                }
            }

            return cron_schedule_action('check', show_schedule, error_callback, {schedule: schedule});
        }
    };

    function cron_schedule_action(action, on_success, on_error, data) {
        // Helper function to access the /schedule/ACTION endpoint

        var settings = common.AjaxSettings({
            data: data || {},
            type: 'POST',
            success: common.SuccessWrapper(on_success, on_error),
            error: on_error
        });

        var url = urls.api_url + utils.url_join_encode(
            'schedule', action);
        return utils.ajax(url, settings);
    }

    var notebook = {
        gen_papermill_param: function (path, input, output, cwd, env, activate, kernel, parameters) {
            var error_callback = common.MakeErrorCallback('Error Checking Schedule', 'An error occurred while processing "' + path + '"');

            function build_papermill(data, status, xhr) {
                input.val(data.input || "")
                output.val(data.output || "")
                cwd.val(data.cwd || "")
                env.val(data.env || "")
                activate.val(data.activate || "")
                kernel.val(data.kernel || "")
                const param = data.parameters || {}
                parameters.empty()
                let typed_value = ""
                for (const [key, value] of Object.entries(param)) {
                    if (typeof value === 'string')
                        typed_value = common.escapeSpecialChars(value)
                    else if (typeof value === 'boolean' && data.kernel.startsWith("py"))
                        typed_value = value.toString().charAt(0).toUpperCase() + value.toString().slice(1);
                    else
                        typed_value = value
                    parameters.append($('<div class="list_item row"/>')
                        .append($('<div class="col-xs-5" />')
                            .append($('<input id="notebook_parameters_key[]" class="long-input-field" />').val(key)))
                        .append($('<div class="col-xs-5" />')
                            .append($('<input id="notebook_parameters_value[]" class="long-input-field" />').val(typed_value)))
                        .append($('<div class="col-xs-2" />')
                                    .append($('<input id="notebook_parameters_raw[]" type="checkbox"/>')))
                    )
                }
            }


            return cron_notebook_action('papermill', build_papermill, error_callback, {path: path});
        }
    }

    function cron_notebook_action(action, on_success, on_error, data) {
        // Helper function to access the /notebook/ACTION endpoint

        var settings = common.AjaxSettings({
            data: data || {},
            type: 'POST',
            success: common.SuccessWrapper(on_success, on_error),
            error: on_error
        });

        var url = urls.api_url + utils.url_join_encode(
            'notebook', action);
        return utils.ajax(url, settings);
    }

    return {
        'jobs': jobs,
        'schedule': schedule,
        'notebook': notebook,
        'config': config
    };
});
