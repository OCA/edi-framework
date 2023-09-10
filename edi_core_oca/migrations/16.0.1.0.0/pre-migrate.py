# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from psycopg2 import sql

from odoo import SUPERUSER_ID, api, tools

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    rename_disable_auto_columns(env)


def rename_disable_auto_columns(env):
    tables = _get_consumer_model_tables(env)
    for table in tables:
        if tools.sql.column_exists(env.cr, table, "disable_edi_auto"):
            env.cr.execute(_make_query(table))
            _logger.info(
                "table %s: renamed column `disable_edi_auto` to `edi_disable_auto`"
            )


def _make_query(table):
    return sql.SQL(
        "ALTER TABLE {} RENAME COLUMN 'disable_edi_auto' TO 'edi_disable_auto'"
    ).format(
        sql.Identifier(table),
    )


def _get_consumer_model_tables(env):
    tables = []
    mixin = "edi.exchange.consumer.mixin"
    for model in env.values():
        if model._name != mixin and not model._abstract and mixin in model._inherit:
            tables.append(model._table)
    return tables
