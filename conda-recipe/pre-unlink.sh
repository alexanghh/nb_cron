{
  "${PREFIX}/bin/jupyter" nbextension disable nb_cron --py --sys-prefix
  "${PREFIX}/bin/jupyter" serverextension disable nb_cron --py --sys-prefix
} >>"$PREFIX/.messages.txt" 2>&1
