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
    'services/config',
    './common',
    './urls',
    './models',
    './views',
], function (require, $, Jupyter, utils, configmod, common, urls, models, views) {
    "use strict";

    var conf = new configmod.ConfigSection('common', {base_url: utils.get_body_data("baseUrl")});
    conf.loaded.then(function () {
        if (Jupyter.notebook_list && conf.data.nb_cron.hasOwnProperty('papermill_path')) {
            var papermill_path = conf.data.nb_cron.papermill_path;
            if (papermill_path) {
                console.log("[nb_cron] papermill_path:", papermill_path);
                models.config.papermill_path = papermill_path;
            }
        }
        if (Jupyter.notebook_list && conf.data.nb_cron.hasOwnProperty('exec_start_pre')) {
            var exec_start_pre = conf.data.nb_cron.exec_start_pre;
            if (exec_start_pre) {
                console.log("[nb_cron] exec_start_pre:", exec_start_pre);
                models.config.exec_start_pre = exec_start_pre;
            }
        }
        if (Jupyter.notebook_list && conf.data.nb_cron.hasOwnProperty('exec_start_post')) {
            var exec_start_post = conf.data.nb_cron.exec_start_post;
            if (exec_start_post) {
                console.log("[nb_cron] exec_start_post:", exec_start_post);
                models.config.exec_start_post = exec_start_post;
            }
        }
        if (Jupyter.notebook_list && conf.data.nb_cron.hasOwnProperty('disable_papermill_log_builder')) {
            var disable_papermill_log_builder = conf.data.nb_cron.disable_papermill_log_builder;
            console.log("[nb_cron] disable_papermill_log_builder:", disable_papermill_log_builder);
            models.config.disable_papermill_log_builder = disable_papermill_log_builder;
        }
    });

    function load() {
        if (!Jupyter.notebook_list) return;

        conf.load();

        $('head').append(
            $('<link>')
                .attr('rel', 'stylesheet')
                .attr('type', 'text/css')
                .attr('href', urls.static_url + 'cron.css')
        );

        utils.ajax(urls.static_url + 'cron.html', {
            dataType: 'html',
            success: function (job_html, status, xhr) {
                // Configure Cron tab
                $(".tab-content").append($(job_html));
                $("#tabs").append(
                    $('<li>')
                        .append(
                            $('<a>')
                                .attr('id', 'cron_tab')
                                .attr('href', '#cron')
                                .attr('data-toggle', 'tab')
                                .text('Cron')
                                .click(function (e) {
                                    window.history.pushState(null, null, '#cron');

                                    models.jobs.load();
                                })
                        )
                );

                views.JobView.init();
                models.jobs.view = views.JobView;

                if (window.location.hash === '#cron') {
                    $('#cron_tab').click();
                }
            }
        });
    }

    return {
        load_ipython_extension: load
    };
});
