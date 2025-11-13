from typing_extensions import Self

from .. import api
from ..api import OdooVersion


class TestOdooConfigSection(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.enable = False
        self.test_tags = None
        self.test_file = None

    def init(self, curr_env: api.Env) -> Self:
        self.enable = curr_env.get_bool("TEST_ENABLE")
        self.test_tags = curr_env.get("TEST_TAGS")
        if curr_env.odoo_version <= OdooVersion.V11.value:
            self.test_tags = None  # Not supported in Odoo 11 or less
        self.test_file = curr_env.get("TEST_FILE")
        return self

    def to_values(self) -> api.OdooCliFlag:
        res = api.OdooCliFlag()
        res.set("test-enable", self.enable)
        if not self.enable:
            return res
        res.set("test-tags", self.test_tags)
        res.set("test-file", self.test_file)
        return res
