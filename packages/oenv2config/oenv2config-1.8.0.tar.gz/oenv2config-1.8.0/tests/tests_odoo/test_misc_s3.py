import unittest

from tests import _decorators

from ._helpers import assertParser, create_config


@_decorators.SkipUnless.env_odoo
class TestMiscS3(unittest.TestCase):
    def test_filestore_s3(self):
        """
        Assert module `odoo_filestore_s3` is enable.
        Returns:

        """
        parser = create_config(["filestore_s3"])
        assertParser(
            self,
            parser,
            {
                "server_wide_modules": ["odoo_filestore_s3"],
            },
        )
        assertParser(
            self,
            parser,
            {
                "s3_access_key": "s3_filestore_access_key",
                "s3_secret": "s3_filestore_secret_key",
                "s3_region": "s3_filestore_region",
                "s3_host": "s3_filestore_host",
                "s3_bucket_name": "s3_filestore_bucket",
                "s3_secure": True,
                "sub_dir_by_dbname": False,
            },
            section="odoo_s3_filestore",
        )

    def test_filestore_s3_cellar(self):
        parser = create_config(["filestore_s3_cellar"])
        assertParser(
            self,
            parser,
            {
                "server_wide_modules": ["odoo_filestore_s3"],
            },
        )
        assertParser(
            self,
            parser,
            {
                "s3_access_key": "qsdlkqjsdlkq",
                "s3_secret": "qsdklqjsdlqksdj",
                "s3_host": "cellar-c2.services.clever-cloud.com",
                "s3_bucket_name": "cellar_s3_filestore_bucket",
                "s3_secure": True,
                "sub_dir_by_dbname": True,
            },
            section="odoo_s3_filestore",
        )
