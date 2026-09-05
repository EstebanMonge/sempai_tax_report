# -*- coding: utf-8 -*-

from odoo import api, models


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report.sempai_tax_report_document'
    _description = 'Sempai Space Tax Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        wizard = self.env['sempai.tax.report.wizard'].browse(docids)

        values = wizard._compute_report_values(data)

        values.update({
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.wizard',
            'docs': wizard,
        })

        return values
