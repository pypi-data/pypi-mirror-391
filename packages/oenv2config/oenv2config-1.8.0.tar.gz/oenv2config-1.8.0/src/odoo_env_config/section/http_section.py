from typing import Union

from typing_extensions import Self

from .. import api
from ..api import OdooVersion


class HttpOdooConfigSection(api.EnvConfigSection):
    """
    This section contains the mapping of `HTTP Service Configuration` from the odoo config parser
    """

    def __init__(self):
        super().__init__()
        self.enable: bool = False
        self.proxy_mode: bool = False
        self.interface: Union[str, None] = None
        self.port: int = 0
        self.longpolling_port: int = 0
        self.enable_x_sendfile: bool = False
        self._gevent_config_name = "longpolling-port"

    def init(self, curr_env: api.Env) -> Self:
        self.enable = curr_env.get_bool("HTTP_ENABLE", default=True)
        self.interface = curr_env.get("HTTP_INTERFACE")
        self.port = curr_env.get_int("HTTP_PORT")
        self.proxy_mode = curr_env.get_bool("PROXY_ENABLE", "PROXY_MODE")
        self.longpolling_port = curr_env.get_int("LONGPOLLING_PORT")
        if curr_env.odoo_version_type >= OdooVersion.V16:
            self._gevent_config_name = "gevent-port"
        if curr_env.odoo_version_type >= OdooVersion.V16:
            self.enable_x_sendfile = curr_env.get_bool("X_SENDFILE")
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = api.OdooCliFlag()
        if not self.enable:
            return res.set("no-http", True)

        res.set("http-interface", self.interface)
        res.set("http-port", self.port)
        res.set(self._gevent_config_name or "", self.longpolling_port)
        res.set("x-sendfile", self.enable_x_sendfile)
        res.set("proxy-mode", self.proxy_mode)
        return res
