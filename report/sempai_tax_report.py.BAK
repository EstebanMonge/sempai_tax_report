# -*- coding: utf-8 -*-

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report.sempai_tax_report_document'
    _description = 'Sempai Space Tax Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        data = data or {}

        date_start = data.get('date_start')
        date_end = data.get('date_end')

        # ============================================================
        # SALES INVOICES
        # ============================================================

        invoice_domain = [
            ('invoice_date', '>=', date_start),
            ('invoice_date', '<=', date_end),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('state_tributacion', '=', 'aceptado'),
        ]

        invoices = self.env['account.move'].search(
            invoice_domain,
            order='partner_id, invoice_date, id'
        )

        # ============================================================
        # PURCHASE INVOICES
        # ============================================================

        purchase_domain = [
            ('invoice_date', '>=', date_start),
            ('invoice_date', '<=', date_end),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ]

        purchases = self.env['account.move'].search(
            purchase_domain,
            order='partner_id, invoice_date, id'
        )

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
            'Accepted sales invoices found: %s',
            len(invoices),
        )
        _logger.info(
            'Accepted purchase invoices found: %s',
            len(purchases),
        )

        for invoice in invoices:
            _logger.info(
                'SALES Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Tributacion=%s | State=%s | Type=%s | Amount Total=%s',
                invoice.id,
                invoice.name,
                invoice.invoice_date,
                invoice.partner_id.display_name,
                invoice.state_tributacion,
                invoice.state,
                invoice.move_type,
                invoice.amount_total,
            )

        for purchase in purchases:
            _logger.info(
                'PURCHASE Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
                'Tributacion=%s | State=%s | Type=%s | Amount Total=%s',
                purchase.id,
                purchase.name,
                purchase.invoice_date,
                purchase.partner_id.display_name,
                purchase.state_tributacion,
                purchase.state,
                purchase.move_type,
                purchase.amount_total,
            )

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # SALES TAX GROUP CALCULATION
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

                        tax_groups[group_id]['subtotal'] += tax_base
                        tax_groups[group_id]['tax'] += tax_amount
                        tax_groups[group_id]['total'] += (
                            tax_base + tax_amount
                        )

        # ============================================================
        # SALES TAX GROUP LOG
        # ============================================================

        _logger.info(
            'TAX GROUP SUMMARY'
        )

        for group_id, values in tax_groups.items():

            _logger.info(
                'Tax Group ID=%s | Name=%s | Subtotal=%s | Tax=%s | Total=%s',
                group_id,
                values['name'],
                values['subtotal'],
                values['tax'],
                values['total'],
            )

        # ============================================================
        # PURCHASE TAX GROUP CALCULATION
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

                        purchase_tax_groups[group_id]['subtotal'] += tax_base
                        purchase_tax_groups[group_id]['tax'] += tax_amount
                        purchase_tax_groups[group_id]['total'] += (
                            tax_base + tax_amount
                        )

        # ============================================================
        # PURCHASE TAX GROUP LOG
        # ============================================================

        _logger.info(
            'PURCHASE TAX GROUP SUMMARY'
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

        _logger.info(
            '============================================================'
        )

        # ============================================================
        # WIZARD DOCUMENT
        # ============================================================

        wizard = self.env['sempai.tax.report.wizard'].browse(docids)

        # ============================================================
        # REPORT VALUES
        # ============================================================

        return {
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.wizard',
            'docs': wizard,
            'invoices': invoices,
            'purchases': purchases,
            'date_start': date_start,
            'date_end': date_end,
            'tax_groups': tax_groups,
            'purchase_tax_groups': purchase_tax_groups,
        }

