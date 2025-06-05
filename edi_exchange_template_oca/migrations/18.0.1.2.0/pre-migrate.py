# Copyright 2025 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib.openupgrade import logged_query

from odoo.tools.sql import column_exists, create_column, table_exists


def migrate(cr, version):
    if not version:
        return
    if table_exists(cr, "edi_exchange_template_type_rel"):
        # If the table already exists, we assume
        # that the migration has already been applied.
        # No need to proceed further.
        return
    # Create the table edi_exchange_template_type_rel
    query = """CREATE TABLE edi_exchange_template_type_rel
    (template_id INT4, type_id INT4)"""
    logged_query(cr, query)

    if not column_exists(cr, "edi_exchange_type", "output_template_id"):
        create_column(cr, "edi_exchange_type", "output_template_id", "int4")

    # Following quiries:
    # 1. Look for templates with a type set and
    # update each exchange type to point to its template
    # 2. Insert the allowed relation between the template and the type
    # 3. Remove the legacy link by setting type_id to NULL
    # 4. Look for types without a template and
    # find the template by code to set as output template
    query_upd_type_1 = """
        UPDATE edi_exchange_type AS exchange_type
        SET output_template_id = exchange_template.id
        FROM edi_exchange_template_output AS exchange_template
        WHERE exchange_template.type_id IS NOT NULL
        AND exchange_type.id = exchange_template.type_id;
    """
    logged_query(cr, query_upd_type_1)

    query_insert_allowed_type = """
        INSERT INTO edi_exchange_template_type_rel (template_id, type_id)
        SELECT id, type_id
        FROM edi_exchange_template_output
        WHERE type_id IS NOT NULL;
    """
    logged_query(cr, query_insert_allowed_type)

    query_remove_legacy_link = """
        UPDATE edi_exchange_template_output
        SET type_id = NULL
        WHERE type_id IS NOT NULL;
    """
    logged_query(cr, query_remove_legacy_link)
    # pylint: disable=W1401
    query_upd_type_2 = """
    WITH valid_templates AS (
        SELECT code,
            backend_type_id,
            MIN(id) AS template_id,
            COUNT(*) AS cnt
        FROM edi_exchange_template_output
        GROUP BY code, backend_type_id
        HAVING COUNT(*) = 1
    )
    UPDATE edi_exchange_type AS exchange_type
    SET output_template_id = vt.template_id
    FROM valid_templates AS vt
    WHERE exchange_type.output_template_id IS NULL
    AND substring(
        exchange_type.advanced_settings_edit
        from 'usage:\s*([^ \n]+)'
        ) = vt.code
    AND exchange_type.backend_type_id = vt.backend_type_id;
    """
    logged_query(cr, query_upd_type_2)
