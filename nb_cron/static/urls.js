/*
 * Copyright (c) 2021, nb_cron Contributors
 *
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file LICENSE, distributed with this software.
 */
define(["base/js/namespace"], function(Jupyter){
    var base_url = (Jupyter.notebook_list || Jupyter.notebook).base_url;
    var api_url = base_url + "cron/";
    var static_url = base_url + "nbextensions/nb_cron/";

    return {
        base_url: base_url,
        api_url: api_url,
        static_url: static_url
    };
});
