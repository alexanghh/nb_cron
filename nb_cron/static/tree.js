define([
    'require',
    'jquery',
    'base/js/namespace',
    'base/js/utils',
    './common',
    './urls',
    './models',
    './views',
], function(require, $, Jupyter, utils, common, urls, models, views) {
    "use strict";

    function load() {
        console.log('loading tree.js')
        console.log("tree.load.models: " + models)

        if (!Jupyter.notebook_list) return;
        var base_url = Jupyter.notebook_list.base_url;
        $('head').append(
            $('<link>')
            .attr('rel', 'stylesheet')
            .attr('type', 'text/css')
            .attr('href', urls.static_url + 'cron.css')
        );

        console.log("tree.load.models: " + models)

        utils.ajax(urls.static_url + 'cron.html', {
            dataType: 'html',
            success: function(job_html, status, xhr) {
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

                console.log("tree.load.models2: " + models)
                views.JobView.init();
                models.jobs.view = views.JobView;

                if(window.location.hash === '#cron') {
                    $('#cron_tab').click();
                }
            }
        });
    }
    return {
        load_ipython_extension: load
    };
});
