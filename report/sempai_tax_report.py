# -*- coding: utf-8 -*-

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SempaiTaxReport(models.AbstractModel):
    _name = 'report.sempai_tax_report.sempai_tax_report_document'

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
        sales_totals = {
            'untaxed': sum(invoice.amount_untaxed for invoice in invoices),
            'tax': sum(invoice.amount_tax for invoice in invoices),
            'total': sum(invoice.amount_total for invoice in invoices),
        }

        purchase_totals = {
            'untaxed': sum(purchase.amount_untaxed for purchase in purchases),
            'tax': sum(purchase.amount_tax for purchase in purchases),
            'total': sum(purchase.amount_total for purchase in purchases),
        }
        # ============================================================
        # SALES TAX GROUP CALCULATION
        # ============================================================

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
        # TAX GROUP LOG
        # ============================================================

        _logger.info(
            '============================================================'
        )
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

        _logger.info(
            '============================================================'
        )
        # ============================================================
        # PURCHASE TAX GROUP CALCULATION
        # ============================================================
        purchase_tax_groups = {}
     
        for purchase in purchases:
            for line in purchase.invoice_line_ids:
         
                for tax in line.invoice_line_tax_ids:
         
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
        _logger.info(
            '============================================================'
        )
     
        _logger.info(
            'PURCHASE TAX GROUP SUMMARY'
        )
     
        for group_id, values in purchase_tax_groups.items():
     
            _logger.info(
                'Purchase Tax Group ID=%s | Name=%s | Subtotal=%s | Tax=%s | Total=%s',
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
        # REPORT DATA LOG
        # ============================================================

        _logger.info(
            'REPORT DATA'
        )

        _logger.info(
            'Invoice IDs: %s',
            invoice_ids,
        )

        _logger.info(
            'Date range: %s -> %s',
            date_start,
            date_end,
        )

        _logger.info(
            'Invoices found in report: %s',
            len(invoices),
        )

        for invoice in invoices:

            _logger.info(
                'REPORT Invoice ID=%s | Number=%s | Date=%s | Partner=%s | '
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

        # ============================================================
        # REPORT VALUES
        # ============================================================

        return {
            'doc_ids': docids,
            'doc_model': 'sempai.tax.report.wizard',
            'docs': self.env['sempai.tax.report.wizard'].browse(
                data.get('context', {}).get('active_ids', [])
            ),
            'invoices': invoices,
            'purchases': purchases,
            'date_start': date_start,
            'date_end': date_end,
            'tax_groups': tax_groups,
            'purchase_tax_groups': purchase_tax_groups,
            'sales_totals': sales_totals,
            'purchase_totals': purchase_totals,
        }
