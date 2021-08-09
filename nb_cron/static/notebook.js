/*
 * Copyright (c) 2021, nb_cron Contributors
 *
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file LICENSE, distributed with this software.
 */
define([
    'require',
    'jquery',
    'base/js/namespace',
    'base/js/utils',
    'base/js/dialog',
    'services/config',
    './common',
    './urls',
    './models',
    './views',
], function (require, $, Jupyter, utils, dialog, configmod, common, urls, models, views) {
    "use strict";

    var $view = $('#cron');

    var conf = new configmod.ConfigSection('common', {base_url: utils.get_body_data("baseUrl")});
    conf.loaded.then(function () {
        if (Jupyter.notebook && conf.data.hasOwnProperty('papermill_path')) {
            var papermill_path = conf.data.papermill_path;
            if (papermill_path) {
                console.log("papermill_path:", papermill_path);
                models.config.papermill_path = papermill_path;
            }
        }
    });

    function show_cron_view($view) {
        var d = dialog.modal({
            title: 'Cron job list',
            body: $view,
            open: function () {
                $('#refresh_job_list').click();
            },
            keyboard_manager: Jupyter.notebook.keyboard_manager
        });
        d.on('hide.bs.modal', function () {
            // detach the cron view so it isn't destroyed with the dialog box
            $view.detach();
        });
        d.find('.modal-dialog').css({width: "80vw"});
    }

    function load_cron_view() {
        if ($view.length === 0) {
            // Not loaded yet
            utils.ajax(urls.static_url + 'cron.html', {
                dataType: 'html',
                success: function (cron_html, status, xhr) {
                    // Load the 'cron tab'
                    $view = $(cron_html);
                    $('body').append($view);

                    views.JobView.init();
                    models.jobs.view = views.JobView;

                    show_cron_view($view);
                }
            });
        } else {
            show_cron_view($view);
        }
    }

    function show_add_cron_view() {

        function job_callback(schedule, command, comment) {
            models.jobs.create(schedule, command, comment)
        }

        var title = 'New Job'

        var jobDialog = views.prompts.jobPrompt(title, job_callback);
        jobDialog.find('#job_comment').val('cron job for ' + Jupyter.notebook.notebook_name);

        var papermillDialog = views.prompts.papermillBuilderPrompt(jobDialog.find('#job_command'), title);
        papermillDialog.find('#notebook_input').val(Jupyter.notebook.notebook_path);
        Jupyter.notebook
        papermillDialog.find('#inspect_notebook').trigger($.Event("click"));
    }

    function editJob(job) {
        function callback(schedule, command, comment) {
            models.jobs.edit(job, schedule, command, comment).then(function () {
                check_notebook_scheduled();
            });
        }

        views.prompts.jobPrompt('Edit Job', callback, job.schedule, job.command, job.comment);
    }

    function check_notebook_scheduled() {
        $('#cron_edit_notebook').off("click");
        models.jobs.load().then(function () {
            var data = models.jobs.all
            $('#cron_edit_notebook').hide();
            $.each(data, function (index, row) {
                if (row['command'].indexOf(Jupyter.notebook.notebook_path) >= 0) {
                    $('#cron_edit_notebook').click(function () {
                        editJob(row);
                    });
                    $('#cron_edit_notebook').show();
                    return false;
                }
            });
        });
    }

    function load() {
        if (!Jupyter.notebook) return;

        conf.load()

        $('head').append(
            $('<link>')
                .attr('rel', 'stylesheet')
                .attr('type', 'text/css')
                .attr('href', urls.static_url + 'cron.css')
        );

        utils.ajax(urls.static_url + 'menu.html', {
            dataType: 'html',
            success: function (menu_html, status, xhr) {

                // Add cron in menu
                var cron_menu = $('<li>').addClass('dropdown');
                cron_menu.append('<a class="dropdown-toggle" data-toggle="dropdown">Cron</a>');
                cron_menu.append($('<ul>').addClass('dropdown-menu').append($(menu_html)));

                $('ul.nav.navbar-nav').append(cron_menu);
                $('#cron_job_list').click(load_cron_view);
                $('#cron_schedule_notebook').click(show_add_cron_view);

                check_notebook_scheduled();
            }
        });
    }

    return {
        load_ipython_extension: load
    };
});
