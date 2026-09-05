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

        # ============================================================
        # SALES
        # ============================================================

        company = self.env.user.company_id

        sales_domain = [
            ('company_id', '=', company.id),
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
        ]

        # Simplified regimen companies (electronic invoicing disabled)
        # never populate state_tributacion, so it must not be used to
        # filter their invoices.
        if company.frm_ws_ambiente != 'disabled':
            sales_domain.append(('state_tributacion', '=', 'aceptado'))

        invoices = self.env['account.move'].search(sales_domain).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.invoice_date or '',
            )
        )

        # ============================================================
        # PURCHASES
        # ============================================================

        purchases = self.env['account.move'].search([
            ('company_id', '=', company.id),
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('state', '=', 'posted'),
            ('move_type', '=', 'in_invoice'),
        ]).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.invoice_date or '',
            )
        )

        # ============================================================
        # SALES LOG
        # ============================================================

        _logger.info(
            '============================================================'
        )
        _logger.info(
            'SEMPAI TAX REPORT - SALES INVOICE SEARCH'
        )
        _logger.info(
            'Company ID: %s',
            company.id,
        )
        _logger.info(
            'Company: %s',
            company.name,
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
                'State=%s | Move Type=%s | Tributacion=%s | '
                'Amount Total=%s',
                invoice.id,
                invoice.name,
                invoice.invoice_date,
                invoice.partner_id.display_name
                if invoice.partner_id else '',
                invoice.state,
                invoice.move_type,
                invoice.state_tributacion,
                invoice.amount_total,
            )

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # PURCHASE LOG
        # ============================================================

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
                'State=%s | Move Type=%s | Amount Total=%s',
                purchase.id,
                purchase.name,
                purchase.invoice_date,
                purchase.partner_id.display_name
                if purchase.partner_id else '',
                purchase.state,
                purchase.move_type,
                purchase.amount_total,
            )

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # REPORT
        # ============================================================

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
