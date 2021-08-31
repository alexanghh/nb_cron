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
        if (Jupyter.notebook && conf.data.nb_cron.hasOwnProperty('papermill_path')) {
            var papermill_path = conf.data.nb_cron.papermill_path;
            if (papermill_path) {
                console.log("[nb_cron] papermill_path:", papermill_path);
                models.config.papermill_path = papermill_path;
            }
        }
        if (Jupyter.notebook && conf.data.nb_cron.hasOwnProperty('exec_start_pre')) {
            var exec_start_pre = conf.data.nb_cron.exec_start_pre;
            if (exec_start_pre) {
                console.log("[nb_cron] exec_start_pre:", exec_start_pre);
                models.config.exec_start_pre = exec_start_pre;
            }
        }
        if (Jupyter.notebook && conf.data.nb_cron.hasOwnProperty('exec_start_post')) {
            var exec_start_post = conf.data.nb_cron.exec_start_post;
            if (exec_start_post) {
                console.log("[nb_cron] exec_start_post:", exec_start_post);
                models.config.exec_start_post = exec_start_post;
            }
        }
        if (Jupyter.notebook && conf.data.nb_cron.hasOwnProperty('disable_papermill_log_builder')) {
            var disable_papermill_log_builder = conf.data.nb_cron.disable_papermill_log_builder;
            console.log("[nb_cron] disable_papermill_log_builder:", disable_papermill_log_builder);
            models.config.disable_papermill_log_builder = disable_papermill_log_builder;
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

        // save notebook before inspection
        Jupyter.notebook.save_checkpoint().then(function () {

            function job_callback(schedule, command, comment) {
                models.jobs.create(schedule, command, comment)
            }

            var title = 'New Job';

            var jobDialog = views.prompts.jobPrompt(title, job_callback);
            jobDialog.find('#job_comment').val('cron job for ' + Jupyter.notebook.notebook_name);

            var papermillDialog = views.prompts.papermillBuilderPrompt(jobDialog.find('#job_command'), title);
            papermillDialog.find('#notebook_input').val(Jupyter.notebook.notebook_path);
            papermillDialog.find('#inspect_notebook').trigger($.Event("click"));
        });
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

    function set_papermill_parameters_cell() {
        // clear parameters tag from all cell
        Jupyter.notebook.get_cells().forEach(function (cell) {
            // Remove from metadata
            if (cell.metadata && cell.metadata.tags) {
                // Remove tag from tags list
                var index = cell.metadata.tags.indexOf("parameters");
                if (index !== -1) {
                    console.log("parameters found in cell");
                    cell.metadata.tags.splice(index, 1);
                }
                // If tags list is empty, remove it
                if (cell.metadata.tags.length === 0) {
                    delete cell.metadata.tags;
                }
            }
        })

        // add parameters tag to selected cell
        var cell = Jupyter.notebook.get_selected_cell();
        if (cell.metadata.tags) {
            if (!cell.metadata.tags.includes("parameters"))
                cell.metadata.tags.push("parameters");
        } else
            cell.metadata.tags = ["parameters"]
        Jupyter.CellToolbar.activate_preset("Tags");
        Jupyter.CellToolbar.global_hide()
        Jupyter.CellToolbar.global_show()
        Jupyter.notebook.metadata.celltoolbar = "Tags"

        Jupyter.notebook.save_checkpoint()
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
                $('#cron_set_parameter_cell').click(set_papermill_parameters_cell);

                check_notebook_scheduled();
            }
        });
    }

    return {
        load_ipython_extension: load
    };
});
