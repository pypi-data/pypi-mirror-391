from typing_extensions import Self

from .. import api


class S3Section(api.EnvConfigSection):
    def __init__(self):
        super().__init__()
        self.access_key = False
        self.secret = False
        self.region = False
        self.host = False
        self.bucket_name = False
        self.secure = False
        self.sub_dir = False

    def init(self, curr_env: api.Env) -> Self:
        self.access_key = curr_env.get("S3_FILESTORE_ACCESS_KEY")
        self.secret = curr_env.get("S3_FILESTORE_SECRET_KEY")
        self.region = curr_env.get("S3_FILESTORE_REGION")
        self.host = curr_env.get("S3_FILESTORE_HOST")
        self.bucket_name = curr_env.get("S3_FILESTORE_BUCKET")
        self.secure = curr_env.get_bool("S3_SECURE", default=True)
        self.sub_dir = curr_env.get_bool("S3_FILESTORE_SUB_DIR", default=False)
        return self

    def write_to_config(self, config: api.OdooConfig):
        if not self.host:
            return
        config.misc["odoo_s3_filestore"] = {
            "s3_access_key": self.access_key,
            "s3_secret": self.secret,
            "s3_region": self.region,
            "s3_host": self.host,
            "s3_bucket_name": self.bucket_name,
            "s3_secure": self.secure,
            "sub_dir_by_dbname": self.sub_dir,
        }
