python setup.py develop
jupyter nbextension install nb_cron --py --sys-prefix --symlink
jupyter nbextension enable nb_cron --py --sys-prefix
jupyter serverextension enable nb_cron --py --sys-prefix
