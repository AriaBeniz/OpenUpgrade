# -*- coding: utf-8 -*-
# Developed by Behrouz Mohammadi (Behrouz.m@outlook.com)

import logging

from openupgradelib import openupgrade

logger = logging.getLogger('OpenUpgrade')

column_renames = {
    'res_currency_rate': [
        ('company_id', 'company_id_8'),
    ]
}

field_renames = [
    ('res.currency.rate', 'res_currency_rate', 'company_id', 'company_id_8'),
]

column_copies = {
    '': [
        ('', None, None),
    ],
}

table_renames = [
    ('', ''),
]

xmlid_renames = [
    ('', ''),
]

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    logger.warn(">>> BASE UPGRADE START")
    cr = env.cr
    openupgrade.rename_fields(env, field_renames)
    #openupgrade.rename_columns(cr, column_renames)
    logger.warn("<<< BASE UPGRADE DONE")
    #openupgrade.rename_tables(cr, table_renames)
    #openupgrade.rename_xmlids(cr, xmlid_renames)
    #openupgrade.copy_columns(cr, column_copies)


