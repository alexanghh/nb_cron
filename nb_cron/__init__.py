#############################################################################
# Copyright (c) 2021, nb_cron Contributors                                  #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################
# flake8: noqa
from .handlers import load_jupyter_server_extension
from . import _version
__version__ = _version.get_versions()['version']

def _jupyter_nbextension_paths():
    return [dict(section="notebook",
                 src="static",
                 dest="nb_cron",
                 require="nb_cron/notebook"),
            dict(section="tree",
                 src="static",
                 dest="nb_cron",
                 require="nb_cron/tree")]


def _jupyter_server_extension_paths():
    return [dict(module="nb_cron")]

