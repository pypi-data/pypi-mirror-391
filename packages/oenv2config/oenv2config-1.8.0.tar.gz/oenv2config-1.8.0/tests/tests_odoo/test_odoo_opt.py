import unittest

from tests import _decorators

from ._helpers import assertParser, create_config


@_decorators.SkipUnless.env_odoo
class TestOdooOpt(unittest.TestCase):
    def test_odoo_opt(self):
        """
        Assert module `odoo_filestore_s3` is enable.
        Returns:

        """
        parser = create_config(["odoo_opt"])
        assertParser(
            self,
            parser,
            {
                "modules_auto_install_enabled": "web_responsive",
                "modules_auto_install_disabled": "partner_autocomplete,iap,mail_bot",
            },
        )
