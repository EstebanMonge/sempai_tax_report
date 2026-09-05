# -*- coding: utf-8 -*-

{
    'name': 'Sempai Tax Report',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Sempai tax PDF and Excel Reports',
    'author': 'Sempai Space',
    'depends': [
        'base',
        'report_xlsx',
    ],
    'data': [
        'views/sempai_tax_report_wizard.xml',
        'report/sempai_tax_report_template.xml',
        'report/sempai_tax_report_report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
