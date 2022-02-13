# -*- coding: utf-8 -*-
# Developed by Behrouz Mohammadi (Behrouz.m@outlook.com)

import logging

from openupgradelib import openupgrade

logger = logging.getLogger('OpenUpgrade')

column_renames = {
    '': [
        ('', ''),
    ]
}

field_renames = [
    ('', ''),
]

column_copies = {
    'res_currency_rate': [
        ('company_id_8', 'company_id', None),
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
    cr = env.cr
    #openupgrade.rename_tables(cr, table_renames)
    #openupgrade.rename_columns(cr, column_renames)
    #openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.copy_columns(cr, column_copies)
    #openupgrade.rename_fields(env, field_renames)
