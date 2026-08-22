# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import ValidationError


class SempaiTaxReportWizard(models.TransientModel):
    _name = 'sempai.tax.report.wizard'
    _description = 'Sempai Tax Report Wizard'

    date_start = fields.Date(
        string='Start Date',
        required=True,
    )

    date_end = fields.Date(
        string='End Date',
        required=True,
    )

    def action_print_report(self):

        if self.date_start > self.date_end:
            raise ValidationError(
                'Start Date cannot be greater than End Date.'
            )

        invoices = self.env['account.invoice'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('date_invoice', '>=', self.date_start),
            ('date_invoice', '<=', self.date_end),
            ('state', 'in', ['open', 'paid']),
            ('state_tributacion', '=', 'aceptado'),
            ('type', '=', 'out_invoice'),
        ])

        purchases = self.env['account.invoice'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('date_invoice', '>=', self.date_start),
            ('date_invoice', '<=', self.date_end),
            ('state', 'in', ['open', 'paid']),
            ('type', '=', 'in_invoice'),
        ])

        return self.env.ref(
            'sempai_tax_report.action_sempai_tax_report'
        ).report_action(
            self,
            data={
                'invoice_ids': invoices.ids,
                'purchase_ids': purchases.ids,
                'date_start': self.date_start,
                'date_end': self.date_end,
            }
        )
