from typing import List

from typing_extensions import Self

from .. import api
from ..api import OdooCliFlag


class OdooOptSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.options: List[OdooCliFlag] = []

    def init(self, curr_env: api.Env) -> Self:
        """ """
        for key, value in curr_env.get_start_with("OPT_ODOO_"):
            self.options.append(OdooCliFlag().set(key.lower(), value))
        return self

    def write_to_config(self, config: api.OdooConfig):
        for option in self.options:
            for key, value in option.items():
                config[key]=value
