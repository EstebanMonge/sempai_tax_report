# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

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

        if self.date_start and self.date_end:
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
        ]).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.date_invoice or '',
            )
        )

        purchases = self.env['account.invoice'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('date_invoice', '>=', self.date_start),
            ('date_invoice', '<=', self.date_end),
            ('state', 'in', ['open', 'paid']),
            ('type', '=', 'in_invoice'),
        ]).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.date_invoice or '',
            )
        )

        _logger.info(
            '============================================================'
        )
        _logger.info(
            'SEMPAI TAX REPORT - INVOICE SEARCH'
        )
        _logger.info(
            'Date range: %s -> %s',
            self.date_start,
            self.date_end,
        )
        _logger.info(
            'Invoices found: %s',
            len(invoices),
        )
     
        for invoice in invoices:
            _logger.info(
                'Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'State=%s | Type=%s | Amount Total=%s',
                invoice.id,
                invoice.number,
                invoice.date_invoice,
                invoice.partner_id.display_name,
                invoice.state,
                invoice.type,
                invoice.amount_total,
            )
     
        _logger.info(
            '============================================================'
        )
        _logger.info(
            '============================================================'
        )    
        _logger.info(
            'SEMPAI TAX REPORT - PURCHASE SEARCH'
        )    
        _logger.info(
            'Date range: %s -> %s',
            self.date_start,
            self.date_end,
        )    
        _logger.info(
            'Purchases found: %s',
            len(purchases),
        )    
         
        for purchase in purchases:
            _logger.info(
                'Purchase ID=%s | Number=%s | Date=%s | Partner=%s | '
                'State=%s | Type=%s | Amount Total=%s',
                purchase.id,
                purchase.number,
                purchase.date_invoice,
                purchase.partner_id.display_name,
                purchase.state,
                purchase.type,
                purchase.amount_total,
            )

        _logger.info(
            '============================================================'
        )
    
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
