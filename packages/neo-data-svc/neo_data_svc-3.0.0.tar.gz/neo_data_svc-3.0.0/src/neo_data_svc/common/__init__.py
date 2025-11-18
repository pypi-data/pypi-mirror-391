from dynaconf import Dynaconf

from . import job as NDP_job
from . import system as NDP_sys
from .log import NDS_log

_settings = Dynaconf(envvar_prefix="NDS")


def NDS_get_v(k, v=None):
    return _settings.get(k, v)
