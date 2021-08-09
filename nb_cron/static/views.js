/*
 * Copyright (c) 2021, nb_cron Contributors
 *
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file LICENSE, distributed with this software.
 */
define([
    'jquery',
    'base/js/namespace',
    'base/js/utils',
    './common',
    './models',
], function ($, Jupyter, utils, common, models) {
    "use strict";

    function action_start(btn) {
        var $btn = $(btn);
        $btn.focus();

        var $icon = $btn.find('i');
        var old_classes = $icon.attr('class');
        $icon.attr('class', 'fa fa-spinner fa-spin');
        return old_classes;
    }

    function action_end(btn, old_classes) {
        var $btn = $(btn);
        $btn.blur();
        $btn.find('i').attr('class', old_classes);
    }

    var ListView = {
        selector: null,
        model: null,
        columns: [],      // e.g., [{ heading: 'Name', attr: 'name', width: 3 }]
        label: 'item',
        selectable: false,
        transforms: {},
        bindings: {},

        init: function () {
            this.create_header();
            this.bind();
        },

        bind: function () {
            var $root = $(this.selector);

            $.each(this.bindings, function (selector, callback) {
                $root.find(selector).click(callback);
            });

            $root.find("button[title]").tooltip({
                container: "body",
                placement: "top"
            });
        },

        update_label: function (count) {
            $(this.selector).find('.toolbar_info').text(common.pluralize(count, this.label));
        },

        create_header: function (count) {
            var $header = $(this.selector).find('.list_header');
            $header.empty();

            $.each(this.columns, function (index, column) {
                $('<div/>')
                    .addClass('col-xs-' + column.width)
                    .text(column.heading)
                    .appendTo($header);
            });
        },

        refresh: function (data) {
            var that = this;
            var $root = $(this.selector);

            this.update_label(data.length);
            var $body = $root.find('.list_body');
            $body.empty();

            $.each(data, function (index, row) {
                var $row = $('<div/>')
                    .addClass('list_item')
                    .addClass('row')
                    .data('data', row);

                $.each(that.columns, function (index, column) {
                    var $cell = $('<div/>')
                        .addClass('col-xs-' + column.width);

                    var xform = that.transforms[column.attr];
                    if (xform) {
                        $cell.append(xform(row, $row));
                    } else {
                        // Default is to stuff text in the div
                        $cell.text(row[column.attr]);
                    }

                    $row.append($cell);
                });

                $body.append($row);
            });
        }
    }

    var JobView = Object.create(ListView);

    var prompts = {

        papermillBuilderPrompt: function (command, parent_title) {
            var input = $('<textarea id="notebook_input" class="short-textarea-field"/>');
            var output = $('<textarea id="notebook_output" class="short-textarea-field"/>');
            var cwd = $('<textarea id="notebook_cwd" class="short-textarea-field"/>');
            var env = $('<input id="notebook_env" class="input-field"/>');
            var activate = $('<input type="hidden" id="notebook_env_activate"/>');
            var kernel = $('<input id="notebook_kernel" class="input-field"/>');
            var parameters = $('<div id="notebook_parameters_list_body" class="list_body scrollable">');

            var dialog_form = $('<div/>').addClass('form-style-2').attr('title', "Papermill Command Builder").append(
                $('<form class="notebook_details_form"/>').append($('<fieldset/>')
                    .append($('<label for="notebook_input"><span>Input Notebook</span></label>'))
                    .append(input)
                    .append(common.icon('search').attr('id', 'inspect_notebook').addClass('fa-lg').attr('title', 'Inspect notebook').click(function () {
                        models.notebook.gen_papermill_param(input.val(), input, output, cwd, env, activate, kernel, parameters)
                        return false;
                    }))
                    .append($('<label for="notebook_output"><span>Output Notebook</span></label>'))
                    .append(output)
                    .append($('<label for="notebook_cwd"><span>Working Directory</span></label>'))
                    .append(cwd)
                    .append($('<label for="notebook_env"><span>Env</span></label>'))
                    .append(env)
                    .append(activate)
                    .append($('<label for="notebook_kernel"><span>Kernel</span></label>'))
                    .append(kernel)
                    .append($('<div id="parameters_toolbar" class="list_toolbar row" />')
                        .append($('<div class="col-xs-10 no-padding">').append($('<span><b>Parameters</b></span>')))
                        .append($('<div class="col-xs-2 no-padding tree-buttons">')
                            .append(common.button("Clear variable(s)", "trash").click(function () {
                                parameters.empty();
                                return false;
                            }))
                            .append(common.button("Add variable", "plus").click(function () {
                                parameters.append($('<div class="list_item row"/>')
                                    .append($('<div class="col-xs-5" />')
                                        .append($('<input id="notebook_parameters_key[]" class="long-input-field" />')))
                                    .append($('<div class="col-xs-5" />')
                                        .append($('<input id="notebook_parameters_value[]" class="long-input-field" />')))
                                    .append($('<div class="col-xs-2" />')
                                        .append($('<input id="notebook_parameters_raw[]" type="checkbox"/>')))
                                )
                                return false;
                            }))
                        )
                    )
                    .append($('<div id="notebook_parameters_list" class="list_container"/>')
                        .append($('<div id="notebook_parameters_header" class="list_header row">')
                            .append($('<div class="col-xs-5">Variable</div>'))
                            .append($('<div class="col-xs-5">Value</div>'))
                            .append($('<div class="col-xs-2" title="Force parameter to be string">String?</div>'))
                        )
                        .append(parameters)
                    )
                ));

            function ok() {
                let command_string = models.config.papermill_path + ' "' + $('#notebook_input').val() + '" "' + $('#notebook_output').val() +
                    '" --cwd "' + $('#notebook_cwd').val() + '" --kernel ' + $('#notebook_kernel').val()
                var params_key = $("input[id='notebook_parameters_key[]']").map(function () {
                    return $(this).val();
                }).get();
                var params_value = $("input[id='notebook_parameters_value[]']").map(function () {
                    return $(this).val();
                }).get();
                var params_is_raw = $("input[id='notebook_parameters_raw[]']").map(function () {
                    return $(this)[0].checked;
                }).get();
                for (let i = 0; i < params_key.length; i++) {
                    if (params_key[i] && params_value[i]) {
                        if (params_is_raw[i]) {
                            command_string += ' --parameters_raw ' + params_key[i] + ' ' + common.bashQuote(params_value[i])
                        } else {
                            command_string += ' --parameters ' + params_key[i] + ' ' + common.bashQuote(params_value[i])
                        }
                    }
                }
                if ($('#notebook_env').val() &&  $('#notebook_env_activate').val()) {
                    command_string = '. ' + $('#notebook_env_activate').val() + ' ' + $('#notebook_env').val() + '; ' + command_string
                }
                command.val(command_string);
            }

            var title = "Papermill Command Builder"
            if (parent_title)
                title = parent_title + " - " + title
            return common.confirm(title, dialog_form, 'Build Command', ok, undefined).attr('id', 'papermill_dialog').on("hidden.bs.modal", function () {
                if (Jupyter.notebook)
                    Jupyter.keyboard_manager.disable()
            });
        },

        jobPrompt: function (title, callback, old_schedule, old_command, old_comment) {
            var comment = $('<input id="job_comment" name="comment" class="long-input-field"/>');
            var schedule = $('<input id="job_schedule" name="schedule" class="short-input-field"/>');
            var command = $('<textarea id="job_command" name="command" class="textarea-field"/>');

            if (typeof old_schedule !== 'undefined')
                schedule.val(old_schedule)
            if (typeof old_command !== 'undefined')
                command.val(old_command);
            if (typeof old_comment !== 'undefined')
                comment.val(old_comment)

            var dialog_form = $('<div/>').addClass('form-style-2').attr('title', title).append(
                $('<form class="job_details_form"/>').append(
                    $('<fieldset/>')
                        .append($('<label for="job_comment"><span>Comment</span></label>'))
                        .append(comment)
                        .append($('<label for="job_command">')
                            .append($('<span>')
                                .append($('<span>Command</span><br /><br />'))
                                .append($('<button id="papermill_builder" title="" class="btn btn-default btn-xs">Notebook<br/>Command<br/>Builder</button>').click(function () {
                                    var papermill_dialog = prompts.papermillBuilderPrompt(command, title);
                                    return false;
                                }))))
                        .append(command)
                        .append($('<label for="job_schedule"><span>Schedule' +
                            '<i class="icon-button fa fa-question-circle" title="# Cron schedule syntax: \n' +
                            '# .---------------- minute (0-59) \n' +
                            '# |  .------------- hour (0-23) \n' +
                            '# |  |  .---------- day of month (1-31) \n' +
                            '# |  |  |  .------- month (1-12) OR jan,feb,mar,apr ... \n' +
                            '# |  |  |  |  .---- day of week (0-6) (Sunday=0 or 7) OR sun,mon,tue,wed...\n' +
                            '# |  |  |  |  | \n' +
                            '# * *  * *  *" />' +
                            '</span>'))
                        .append(schedule)
                        .append(common.icon('calendar-check-o').attr('id', 'check_schedule').addClass('fa-lg').attr('title', 'check schedule').click(function () {
                            models.schedule.check($('#job_schedule').val(), $('#job_schedule_list'));
                            return false;
                        }))
                        .append($('<label/>').attr('id', 'job_schedule_list').html(""))
                )
            );

            function ok() {
                callback($('#job_schedule').val(), $('#job_command').val(), $('#job_comment').val());
            }

            return common.confirm(title, dialog_form, 'Submit', ok, undefined).attr('id', 'job_dialog');
        }
    }

    $.extend(JobView, {
        selector: '#jobs',
        label: 'Cron Job',
        selectable: false,
        model: models.jobs,
        columns: [
            {heading: 'Action', attr: '_action', width: '1'},
            {heading: 'Job Id', attr: 'id', width: '1'},
            {heading: 'Comment', attr: 'comment', width: '2'},
            {heading: 'Schedule', attr: 'schedule', width: '2'},
            {heading: 'Command', attr: 'command', width: '6'},
        ],

        transforms: {
            _action: function (row, $row) {
                // This is a pseudo-attribute

                return $('<span class="action_col"/>')
                    .addClass('btn-group')
                    .append(common.icon('edit').click(function () {
                        function callback(schedule, command, comment) {
                            models.jobs.edit(row, schedule, command, comment);
                        }

                        prompts.jobPrompt('Edit Job', callback, row.schedule, row.command, row.comment);
                    }))
                    .append(common.icon('trash-o').click(function () {
                        var msg = 'Are you sure you want to permanently delete job "' + row.id + '" ?';
                        common.confirm('Delete Job', msg, 'Delete', function () {
                            models.jobs.remove(row);
                        });
                    }));
            }
        },

        bindings: {
            '#new_job': function () {
                function callback(schedule, command, comment) {
                    models.jobs.create(schedule, command, comment)
                }

                prompts.jobPrompt('New Job', callback);
            },
            '#refresh_job_list': function () {
                var btn = this;
                var btn_state = action_start(btn);

                models.jobs.load().then(function () {
                    action_end(btn, btn_state);
                });
            },
        }
    });

    return {
        'JobView': JobView,
        'prompts': prompts
    };
});
