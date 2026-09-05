# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields
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

    def _get_report_data(self):

        self.ensure_one()

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

        return {
            'invoice_ids': invoices.ids,
            'purchase_ids': purchases.ids,
            'date_start': self.date_start,
            'date_end': self.date_end,
        }

    def action_print_report(self):

        data = self._get_report_data()

        return self.env.ref(
            'sempai_tax_report.action_sempai_tax_report'
        ).report_action(self, data=data)

    def action_export_xlsx(self):

        data = self._get_report_data()

        return self.env.ref(
            'sempai_tax_report.action_sempai_tax_report_xlsx'
        ).report_action(self, data=data)

    @api.model
    def _compute_report_values(self, data):
        """Shared computation used by both the PDF and Excel renders."""

        data = data or {}

        date_start = data.get('date_start')
        date_end = data.get('date_end')

        invoice_ids = data.get('invoice_ids', [])
        purchase_ids = data.get('purchase_ids', [])

        invoices = self.env['account.move'].browse(invoice_ids).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.invoice_date or '',
            )
        )

        purchases = self.env['account.move'].browse(purchase_ids).sorted(
            key=lambda purchase: (
                purchase.partner_id.name or '',
                purchase.invoice_date or '',
            )
        )

        # ============================================================
        # REPORT CURRENCY
        # ============================================================

        company = self.env.user.company_id
        currency = company.currency_id

        _logger.info(
            '============================================================'
        )

        _logger.info(
            'SEMPAI TAX REPORT'
        )

        _logger.info(
            'Date range: %s -> %s',
            date_start,
            date_end,
        )

        _logger.info(
            'Report currency: %s',
            currency.name,
        )

        _logger.info(
            'Accepted sales invoices found: %s',
            len(invoices),
        )

        _logger.info(
            'Accepted purchase invoices found: %s',
            len(purchases),
        )

        # ============================================================
        # SALES LOG
        # ============================================================

        for invoice in invoices:

            _logger.info(
                'SALES Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Currency=%s | Tributacion=%s | State=%s | Type=%s | '
                'Amount Total=%s',
                invoice.id,
                invoice.name,
                invoice.invoice_date,
                invoice.partner_id.display_name,
                invoice.currency_id.name,
                invoice.state_tributacion,
                invoice.state,
                invoice.move_type,
                invoice.amount_total,
            )

        # ============================================================
        # PURCHASE LOG
        # ============================================================

        for purchase in purchases:

            _logger.info(
                'PURCHASE Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Currency=%s | Tributacion=%s | State=%s | Type=%s | '
                'Amount Total=%s',
                purchase.id,
                purchase.name,
                purchase.invoice_date,
                purchase.partner_id.display_name,
                purchase.currency_id.name,
                purchase.state_tributacion,
                purchase.state,
                purchase.move_type,
                purchase.amount_total,
            )

        # ============================================================
        # SALES TAX GROUP CALCULATION
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        tax_groups = {}

        for invoice in invoices:

            for line in invoice.invoice_line_ids:

                for tax in line.tax_ids:

                    tax_group = tax.tax_group_id

                    if not tax_group:
                        continue

                    group_id = tax_group.id

                    if group_id not in tax_groups:

                        tax_groups[group_id] = {
                            'name': tax_group.name,
                            'subtotal': 0.0,
                            'tax': 0.0,
                            'total': 0.0,
                        }

                    taxes = tax.compute_all(
                        line.price_unit,
                        invoice.currency_id,
                        line.quantity,
                        product=line.product_id,
                        partner=invoice.partner_id,
                    )

                    for tax_value in taxes['taxes']:

                        if tax_value['id'] != tax.id:
                            continue

                        tax_amount = tax_value['amount']
                        tax_base = tax_value['base']

                        # ------------------------------------------------
                        # Convert invoice currency -> company currency
                        # ------------------------------------------------

                        tax_base_company = invoice.currency_id._convert(
                            tax_base,
                            currency,
                            company,
                            invoice.invoice_date,
                            round=False,
                        )

                        tax_amount_company = invoice.currency_id._convert(
                            tax_amount,
                            currency,
                            company,
                            invoice.invoice_date,
                            round=False,
                        )

                        tax_groups[group_id]['subtotal'] += (
                            tax_base_company
                        )

                        tax_groups[group_id]['tax'] += (
                            tax_amount_company
                        )

                        tax_groups[group_id]['total'] += (
                            tax_base_company + tax_amount_company
                        )

        # ============================================================
        # ROUND SALES TAX GROUPS
        # ============================================================

        for values in tax_groups.values():

            values['subtotal'] = currency.round(
                values['subtotal']
            )

            values['tax'] = currency.round(
                values['tax']
            )

            values['total'] = currency.round(
                values['total']
            )

        # ============================================================
        # SALES TAX GROUP LOG
        # ============================================================

        _logger.info(
            'SALES TAX GROUP SUMMARY IN %s',
            currency.name,
        )

        for group_id, values in tax_groups.items():

            _logger.info(
                'Tax Group ID=%s | Name=%s | Subtotal=%s | '
                'Tax=%s | Total=%s',
                group_id,
                values['name'],
                values['subtotal'],
                values['tax'],
                values['total'],
            )

        # ============================================================
        # PURCHASE TAX GROUP CALCULATION
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        purchase_tax_groups = {}

        for purchase in purchases:

            for line in purchase.invoice_line_ids:

                for tax in line.tax_ids:

                    tax_group = tax.tax_group_id

                    if not tax_group:
                        continue

                    group_id = tax_group.id

                    if group_id not in purchase_tax_groups:

                        purchase_tax_groups[group_id] = {
                            'name': tax_group.name,
                            'subtotal': 0.0,
                            'tax': 0.0,
                            'total': 0.0,
                        }

                    taxes = tax.compute_all(
                        line.price_unit,
                        purchase.currency_id,
                        line.quantity,
                        product=line.product_id,
                        partner=purchase.partner_id,
                    )

                    for tax_value in taxes['taxes']:

                        if tax_value['id'] != tax.id:
                            continue

                        tax_amount = tax_value['amount']
                        tax_base = tax_value['base']

                        # ------------------------------------------------
                        # Convert invoice currency -> company currency
                        # ------------------------------------------------

                        tax_base_company = purchase.currency_id._convert(
                            tax_base,
                            currency,
                            company,
                            purchase.invoice_date,
                            round=False,
                        )

                        tax_amount_company = purchase.currency_id._convert(
                            tax_amount,
                            currency,
                            company,
                            purchase.invoice_date,
                            round=False,
                        )

                        purchase_tax_groups[group_id]['subtotal'] += (
                            tax_base_company
                        )

                        purchase_tax_groups[group_id]['tax'] += (
                            tax_amount_company
                        )

                        purchase_tax_groups[group_id]['total'] += (
                            tax_base_company + tax_amount_company
                        )

        # ============================================================
        # ROUND PURCHASE TAX GROUPS
        # ============================================================

        for values in purchase_tax_groups.values():

            values['subtotal'] = currency.round(
                values['subtotal']
            )

            values['tax'] = currency.round(
                values['tax']
            )

            values['total'] = currency.round(
                values['total']
            )

        # ============================================================
        # PURCHASE TAX GROUP LOG
        # ============================================================

        _logger.info(
            'PURCHASE TAX GROUP SUMMARY IN %s',
            currency.name,
        )

        for group_id, values in purchase_tax_groups.items():

            _logger.info(
                'Purchase Tax Group ID=%s | Name=%s | Subtotal=%s | '
                'Tax=%s | Total=%s',
                group_id,
                values['name'],
                values['subtotal'],
                values['tax'],
                values['total'],
            )

        # ============================================================
        # SALES TOTALS
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        sales_subtotal = 0.0
        sales_tax = 0.0
        sales_total = 0.0

        for invoice in invoices:

            sales_subtotal += invoice.currency_id._convert(
                invoice.amount_untaxed,
                currency,
                company,
                invoice.invoice_date,
                round=False,
            )

            sales_tax += invoice.currency_id._convert(
                invoice.amount_tax,
                currency,
                company,
                invoice.invoice_date,
                round=False,
            )

            sales_total += invoice.currency_id._convert(
                invoice.amount_total,
                currency,
                company,
                invoice.invoice_date,
                round=False,
            )

        sales_subtotal = currency.round(sales_subtotal)
        sales_tax = currency.round(sales_tax)
        sales_total = currency.round(sales_total)

        # ============================================================
        # PURCHASE TOTALS
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        purchase_subtotal = 0.0
        purchase_tax = 0.0
        purchase_total = 0.0

        for purchase in purchases:

            purchase_subtotal += purchase.currency_id._convert(
                purchase.amount_untaxed,
                currency,
                company,
                purchase.invoice_date,
                round=False,
            )

            purchase_tax += purchase.currency_id._convert(
                purchase.amount_tax,
                currency,
                company,
                purchase.invoice_date,
                round=False,
            )

            purchase_total += purchase.currency_id._convert(
                purchase.amount_total,
                currency,
                company,
                purchase.invoice_date,
                round=False,
            )

        purchase_subtotal = currency.round(purchase_subtotal)
        purchase_tax = currency.round(purchase_tax)
        purchase_total = currency.round(purchase_total)

        # ============================================================
        # TOTAL LOG
        # ============================================================

        _logger.info(
            '============================================================'
        )

        _logger.info(
            'SALES TOTALS IN %s | Subtotal=%s | Tax=%s | Total=%s',
            currency.name,
            sales_subtotal,
            sales_tax,
            sales_total,
        )

        _logger.info(
            'PURCHASE TOTALS IN %s | Subtotal=%s | Tax=%s | Total=%s',
            currency.name,
            purchase_subtotal,
            purchase_tax,
            purchase_total,
        )

        _logger.info(
            '============================================================'
        )

        return {
            'invoices': invoices,
            'purchases': purchases,

            'date_start': date_start,
            'date_end': date_end,

            'currency': currency,

            'tax_groups': tax_groups,
            'purchase_tax_groups': purchase_tax_groups,

            'sales_subtotal': sales_subtotal,
            'sales_tax': sales_tax,
            'sales_total': sales_total,

            'purchase_subtotal': purchase_subtotal,
            'purchase_tax': purchase_tax,
            'purchase_total': purchase_total,
        }
