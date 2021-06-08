{
  "${PREFIX}/bin/jupyter" nbextension enable nb_cron --py --sys-prefix
  "${PREFIX}/bin/jupyter" serverextension enable nb_cron --py --sys-prefix
} >>"$PREFIX/.messages.txt" 2>&1
ls
