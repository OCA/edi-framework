# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import create_column

from odoo.addons.http_routing.models.ir_http import slugify


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return

    required_modules = ("storage_backend", "edi_storage_oca")
    if not env["ir.module.module"].search(
        [("name", "in", required_modules), ("state", "=", "installed")]
    ):
        return
    if not openupgrade.column_exists(env.cr, "edi_backend", "new_storage_id"):
        create_column(env.cr, "edi_backend", "new_storage_id", "int4")

    _create_fs_storage_records(env)

    if openupgrade.column_exists(env.cr, "edi_backend", "new_storage_id"):
        _column_renames = {
            "edi_backend": [
                ("storage_id", "old_storage_id"),
                ("new_storage_id", "storage_id"),
            ],
        }
        openupgrade.rename_columns(env.cr, _column_renames)


def _create_fs_storage_records(env):
    # Create a fs.storage record for each backend.storage
    storage_backend_records = env["storage.backend"].search([])
    if not storage_backend_records:
        return

    # make sure all backend_type can be mapped even if corresponding modules
    # have not been migrated (on purpose because we should switch to fs_storage)
    selection = [
        ("filesystem", "Filesystem"),
        ("ftp", "FTP"),
        ("sftp", "SFTP"),
        ("s3", "S3"),
    ]
    env["storage.backend"]._fields["backend_type"].selection = selection
    env["storage.backend"]._fields["backend_type_env_default"].selection = selection

    fs_storage = env["fs.storage"]
    for record in storage_backend_records:
        protocol = "file"
        if record.backend_type == "ftp":
            protocol = "ftp"
        elif record.backend_type == "sftp":
            protocol = "sftp"
        elif record.backend_type == "s3":
            protocol = "s3"

        code = slugify(record.name).replace("-", "_")
        if fs_storage.search([("code", "=", code)]):
            code = "%s_%d" % (code, record.id)

        res_id = fs_storage.create(
            {
                "name": record.name,
                "code": code,
                "protocol": protocol,
                "directory_path": record.directory_path,
            }
        )

        env.cr.execute(
            "UPDATE edi_backend SET new_storage_id = %s WHERE storage_id = %s",
            (res_id.id, record.id),
        )
