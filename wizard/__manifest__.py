# -*- coding: utf-8 -*-

{
    'name': 'Sempai Tax Report',
    'version': '12.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Sempai tax PDF Reports',
    'author': 'Sempai Space',
    'depends': [
        'base',
        'accounting_pdf_reports',
        'cr_electronic_invoice',
    ],
    'data': [
        'views/sempai_tax_report_wizard.xml',
        'report/sempai_tax_report_template.xml',
        'report/sempai_tax_report_report.xml',
    ],
    'installable': True,
    'application': False,
}
