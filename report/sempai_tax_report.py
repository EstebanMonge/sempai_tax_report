# -*- coding: utf-8 -*-

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report.sempai_tax_report_document'

    @api.model
    def _compute_tax_groups(self, invoices, currency, company):
        """Group tax amounts of ``invoices`` by tax group, converted to
        ``currency`` (the company currency)."""

        tax_groups = {}

        for invoice in invoices:

            for line in invoice.invoice_line_ids:

                for tax in line.invoice_line_tax_ids:

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

                    price_unit_discounted = line.price_unit * (
                        1 - (line.discount or 0.0) / 100.0
                    )

                    taxes = tax.compute_all(
                        price_unit_discounted,
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
                            invoice.date_invoice,
                            round=False,
                        )

                        tax_amount_company = invoice.currency_id._convert(
                            tax_amount,
                            currency,
                            company,
                            invoice.date_invoice,
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

        return tax_groups

    @api.model
    def _compute_document_totals(self, invoices, currency, company):
        """Return (subtotal, tax, total) for ``invoices``, converted to
        ``currency`` (the company currency)."""

        subtotal = 0.0
        tax = 0.0
        total = 0.0

        for invoice in invoices:

            invoice_date = invoice.date_invoice

            subtotal += invoice.currency_id._convert(
                invoice.amount_untaxed,
                currency,
                company,
                invoice_date,
                round=False,
            )

            tax += invoice.currency_id._convert(
                invoice.amount_tax,
                currency,
                company,
                invoice_date,
                round=False,
            )

            total += invoice.currency_id._convert(
                invoice.amount_total,
                currency,
                company,
                invoice_date,
                round=False,
            )

        return (
            currency.round(subtotal),
            currency.round(tax),
            currency.round(total),
        )

    @api.model
    def _get_report_values(self, docids, data=None):

        data = data or {}

        invoice_ids = data.get('invoice_ids', [])
        purchase_ids = data.get('purchase_ids', [])
        date_start = data.get('date_start')
        date_end = data.get('date_end')

        invoices = self.env['account.invoice'].browse(invoice_ids).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.date_invoice or '',
            )
        )

        purchases = self.env['account.invoice'].browse(purchase_ids).sorted(
            key=lambda invoice: (
                invoice.partner_id.name or '',
                invoice.date_invoice or '',
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
            'Invoices found: %s',
            len(invoices),
        )

        _logger.info(
            'Purchases found: %s',
            len(purchases),
        )

        # ============================================================
        # SALES LOG
        # ============================================================

        for invoice in invoices:

            _logger.info(
                'SALES Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Currency=%s | State=%s | Type=%s | Amount Total=%s',
                invoice.id,
                invoice.number,
                invoice.date_invoice,
                invoice.partner_id.display_name,
                invoice.currency_id.name,
                invoice.state,
                invoice.type,
                invoice.amount_total,
            )

        # ============================================================
        # PURCHASE LOG
        # ============================================================

        for purchase in purchases:

            _logger.info(
                'PURCHASE Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Currency=%s | State=%s | Type=%s | Amount Total=%s',
                purchase.id,
                purchase.number,
                purchase.date_invoice,
                purchase.partner_id.display_name,
                purchase.currency_id.name,
                purchase.state,
                purchase.type,
                purchase.amount_total,
            )

        # ============================================================
        # SALES TAX GROUP CALCULATION
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        tax_groups = self._compute_tax_groups(invoices, currency, company)

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

        purchase_tax_groups = self._compute_tax_groups(
            purchases, currency, company
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

        sales_subtotal, sales_tax, sales_total = (
            self._compute_document_totals(invoices, currency, company)
        )

        # ============================================================
        # PURCHASE TOTALS
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        purchase_subtotal, purchase_tax, purchase_total = (
            self._compute_document_totals(purchases, currency, company)
        )

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

        # ============================================================
        # SALES GROUPED BY ECONOMIC ACTIVITY
        # ALL VALUES ARE CONVERTED TO COMPANY CURRENCY
        # ============================================================

        economic_activities = {}

        for invoice in invoices:

            activity = invoice.economic_activity_id
            activity_id = activity.id or 0

            if activity_id not in economic_activities:

                economic_activities[activity_id] = {
                    'name': activity.name or 'Sin Actividad Económica',
                    'code': activity.code or '',
                    'invoices': self.env['account.invoice'],
                }

            economic_activities[activity_id]['invoices'] |= invoice

        for values in economic_activities.values():

            values['tax_groups'] = self._compute_tax_groups(
                values['invoices'], currency, company
            )

            values['subtotal'], values['tax'], values['total'] = (
                self._compute_document_totals(
                    values['invoices'], currency, company
                )
            )

        economic_activities = sorted(
            economic_activities.values(),
            key=lambda values: values['name'],
        )

        _logger.info(
            'SALES BY ECONOMIC ACTIVITY IN %s',
            currency.name,
        )

        for values in economic_activities:

            _logger.info(
                'Economic Activity=%s (%s) | Invoices=%s | Subtotal=%s | '
                'Tax=%s | Total=%s',
                values['name'],
                values['code'],
                len(values['invoices']),
                values['subtotal'],
                values['tax'],
                values['total'],
            )

        # ============================================================
        # REPORT VALUES
        # ============================================================

        return {
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.wizard',

            'docs': self.env['sempai.tax.report.wizard'].browse(docids),

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

            'economic_activities': economic_activities,
        }
