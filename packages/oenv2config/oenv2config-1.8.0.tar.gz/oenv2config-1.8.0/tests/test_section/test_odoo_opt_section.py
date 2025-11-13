import unittest

from src.odoo_env_config.api import Env, OdooConfig
from src.odoo_env_config.section.odoo_opt_section import OdooOptSection
from typing import cast


class TestOdooOptSection(unittest.TestCase):
    def _prepare_conf(self):
        return OdooOptSection().init(
            Env(
                {
                    "OPT_ODOO_MODULES_AUTO_INSTALL_DISABLED": "partner_autocomplete,iap,mail_bot",
                    "OPT_ODOO_MODULES_AUTO_INSTALL_ENABLED": "web_responsive",
                }
            )
        )

    def test_default(self):
        conf = OdooOptSection()
        self.assertEqual([], conf.options)

    def test_global(self):
        conf = self._prepare_conf()
        self.assertTrue(conf.options)
        self.assertListEqual(["modules_auto_install_disabled", "modules_auto_install_enabled"], [ list(item.keys())[0] for item in conf.options])
        self.assertIn({"modules_auto_install_disabled": "partner_autocomplete,iap,mail_bot"}, conf.options)
        self.assertIn({"modules_auto_install_enabled": "web_responsive"}, conf.options)

    def test_write_to_config(self):
        conf = self._prepare_conf()
        config: OdooConfig = {"db_port": "5469"} # type: ignore
        conf.write_to_config(config)
        self.assertEqual("partner_autocomplete,iap,mail_bot", config["modules_auto_install_disabled"])
        self.assertEqual("web_responsive", config["modules_auto_install_enabled"])
        self.assertEqual("5469", config["db_port"], "pas de changements")
