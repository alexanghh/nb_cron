/*
 * Copyright (c) 2021, nb_cron Contributors
 *
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file LICENSE, distributed with this software.
 */
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith
if (!String.prototype.endsWith) {
    String.prototype.endsWith = function (searchString, position) {
        var subjectString = this.toString();
        if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
            position = subjectString.length;
        }
        position -= searchString.length;
        var lastIndex = subjectString.indexOf(searchString, position);
        return lastIndex !== -1 && lastIndex === position;
    };
}


define([
    'jquery',
    'base/js/namespace',
    'base/js/utils',
    'base/js/dialog',
    'base/js/keyboard',
], function ($, Jupyter, utils, dialog, keyboard) {
    "use strict";

    function SuccessWrapper(success_callback, error_callback) {
        return function (data, status, xhr) {
            if (data.error || data.message) {
                // Conda returned a dict with error info
                error_callback(xhr, status, data.error || data.message);
            } else {
                success_callback(data, status, xhr);
            }
        }
    }

    function MakeErrorCallback(title, msg) {
        return function (xhr, status, e) {
            dialog.modal({
                title: title,

                body: $('<div/>')
                    .addClass('error-header')
                    .text(msg)
                    .append($('<div/>')
                        .addClass('alert alert-danger')
                        .text(e.message || e)),

                buttons: {
                    OK: {
                        'class': 'btn-primary'
                    }
                }
            });
            console.warn(msg + ' ' + e);
            utils.log_ajax_error(xhr, status, e);
        }
    }

    function icon(name) {
        return $('<i/>').addClass('icon-button fa fa-' + name);
    }

    function column(name, width) {
        return $('<div/>').addClass(name + '_col col-xs-' + width)
    }

    function button(title, icon_name) {
        return $('<span class="pull-right">' +
            '<button title="' + title + '" class="btn btn-default btn-xs">' +
            '<i class="fa fa-' + icon_name + '"></i></button></span>');
    }

    function link(url, text) {
        return $('<a href="' + url + '"/>').html(text);
    }

    function AjaxSettings(settings) {
        settings.cache = false;
        settings.dataType = 'json';

        if (!settings.type) {
            settings.type = 'GET';
        }
        return settings;
    }

    function confirm(title, msg, button_text, callback, input) {
        var buttons = {Cancel: {}};
        buttons[button_text] = {
            class: 'btn-danger btn-primary',
            click: callback
        }

        var opts = {
            title: title,
            body: msg,
            buttons: buttons,
        };

        // hack for copy and paste for dialog in notebook
        if (Jupyter.notebook)
            opts['keyboard_manager'] = Jupyter.notebook.keyboard_manager

        var d;

        if (input !== undefined) {
            opts.open = function () {
                // Upon ENTER, click the OK button.
                input.keydown(function (event) {
                    if (event.which === keyboard.keycodes.enter) {
                        d.find('.btn-primary').first().click();
                        return false;
                    }
                });
                input.focus();
            }
        }
        d = dialog.modal(opts);

        return d;
    }


    function prompt(title, msg, label, button_text, callback) {
        var input = $('<input/>').attr('id', 'prompt_name');
        var dialogform = $('<div/>').attr('title', msg).append(
            $('<form/>').append(
                $('<fieldset/>').append(
                    $('<label/>')
                        .attr('for', 'prompt_name')
                        .text(label)
                )
                    .append(input)
            )
        );

        function ok() {
            callback(input.val());
        }

        confirm(title, dialogform, button_text, ok, input);
    }

    function pluralize(count_or_array, single_word, plural_word) {
        var count = (count_or_array instanceof Array) ? count_or_array.length : count_or_array;
        var plural = (count !== 1);
        var word;

        if (plural) {
            if (plural_word) {
                word = plural_word;
            } else {
                if (single_word.endsWith('s') || single_word.endsWith('sh') || single_word.endsWith('ch')) {
                    word = single_word + 'es';
                } else if (single_word.endsWith('y')) {
                    word = single_word.slice(0, -1) + 'ies';
                } else {
                    word = single_word + 's';
                }
            }
        } else {
            word = single_word;
        }
        return count + ' ' + word;
    }

    function escapeSpecialChars(string) {
        return string.replace(/\n/g, "\\n")
            .replace(/\r/g, "\\r")
            .replace(/\t/g, "\\t")
            .replace(/\f/g, "\\f");
    }

    function bashQuote(string) {
        if (string.includes("\\n") ||
            string.includes("\\r") ||
            string.includes("\\t") ||
            string.includes("\\f")) {
            return "$" + quote(string,"'")
        }
        else
            return quote(string)
    }

    function quote(string, quote='"') {
        let re = new RegExp(quote, "g");
        let replacement_quote = "\\" + quote
        return quote + string.replace(re, replacement_quote) + quote;
    }

    return {
        'MakeErrorCallback': MakeErrorCallback,
        'SuccessWrapper': SuccessWrapper,
        'icon': icon,
        'column': column,
        'button': button,
        'link': link,
        'AjaxSettings': AjaxSettings,
        'confirm': confirm,
        'prompt': prompt,
        'pluralize': pluralize,
        'escapeSpecialChars': escapeSpecialChars,
        'quote': quote,
        'bashQuote': bashQuote
    };
});
