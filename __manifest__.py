# -*- coding: utf-8 -*-

{
    'name': 'Sempai Tax Report',
    'version': '20.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Sempai tax PDF and Excel Reports',
    'author': 'Sempai Space',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'report_xlsx',
    ],
    'data': [
        'security/ir.access.csv',
        'views/sempai_tax_report_wizard.xml',
        'report/sempai_tax_report_template.xml',
        'report/sempai_tax_report_report.xml',
    ],
    'installable': True,
    'application': False,
}
