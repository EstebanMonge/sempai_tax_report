# -*- coding: utf-8 -*-

from odoo import models


class SempaiTaxReportXlsx(models.AbstractModel):
    _name = 'report.sempai_tax_report.sempai_tax_report_xlsx'
    _description = 'Sempai Space Tax Report (Excel)'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizards):

        values = self.env['sempai.tax.report.wizard']._compute_report_values(
            data
        )

        sheet = workbook.add_worksheet('Tax Report')

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
        })

        section_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'top': 1,
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1,
        })

        text_format = workbook.add_format({
            'border': 1,
        })

        money_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
        })

        total_label_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
        })

        total_money_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'num_format': '#,##0.00',
        })

        sheet.set_column('A:A', 22)
        sheet.set_column('B:B', 14)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 12)
        sheet.set_column('E:G', 16)

        row = 0

        sheet.write(row, 0, 'Sempai Tax Report', title_format)
        row += 2

        sheet.write(row, 0, 'Start Date:')
        sheet.write(row, 1, str(values['date_start'] or ''))
        row += 1

        sheet.write(row, 0, 'End Date:')
        sheet.write(row, 1, str(values['date_end'] or ''))
        row += 2

        # ============================================================
        # SALES
        # ============================================================

        sheet.write(row, 0, 'Sales', section_format)
        row += 1

        headers = [
            'Invoice', 'Date', 'Partner', 'Currency',
            'Subtotal', 'Taxes', 'Total',
        ]

        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)
        row += 1

        for invoice in values['invoices']:

            sheet.write(row, 0, invoice.name or '', text_format)
            sheet.write(
                row, 1, str(invoice.invoice_date or ''), text_format
            )
            sheet.write(
                row, 2, invoice.partner_id.display_name or '', text_format
            )
            sheet.write(row, 3, invoice.currency_id.name or '', text_format)
            sheet.write(row, 4, invoice.amount_untaxed, money_format)
            sheet.write(row, 5, invoice.amount_tax, money_format)
            sheet.write(row, 6, invoice.amount_total, money_format)
            row += 1

        sheet.merge_range(
            row, 0, row, 3, 'Total Sales', total_label_format
        )
        sheet.write(row, 4, values['sales_subtotal'], total_money_format)
        sheet.write(row, 5, values['sales_tax'], total_money_format)
        sheet.write(row, 6, values['sales_total'], total_money_format)
        row += 3

        # ============================================================
        # SALES TAX SUMMARY
        # ============================================================

        sheet.write(row, 0, 'Sales Tax Summary', section_format)
        row += 1

        for col, header in enumerate(
            ['Tax Group', 'Subtotal', 'Tax', 'Total']
        ):
            sheet.write(row, col, header, header_format)
        row += 1

        for tax_group in values['tax_groups'].values():
            sheet.write(row, 0, tax_group['name'], text_format)
            sheet.write(row, 1, tax_group['subtotal'], money_format)
            sheet.write(row, 2, tax_group['tax'], money_format)
            sheet.write(row, 3, tax_group['total'], money_format)
            row += 1

        row += 2

        # ============================================================
        # PURCHASES
        # ============================================================

        sheet.write(row, 0, 'Purchases', section_format)
        row += 1

        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)
        row += 1

        for purchase in values['purchases']:

            sheet.write(row, 0, purchase.name or '', text_format)
            sheet.write(
                row, 1, str(purchase.invoice_date or ''), text_format
            )
            sheet.write(
                row, 2, purchase.partner_id.display_name or '', text_format
            )
            sheet.write(row, 3, purchase.currency_id.name or '', text_format)
            sheet.write(row, 4, purchase.amount_untaxed, money_format)
            sheet.write(row, 5, purchase.amount_tax, money_format)
            sheet.write(row, 6, purchase.amount_total, money_format)
            row += 1

        sheet.merge_range(
            row, 0, row, 3, 'Total Purchases', total_label_format
        )
        sheet.write(row, 4, values['purchase_subtotal'], total_money_format)
        sheet.write(row, 5, values['purchase_tax'], total_money_format)
        sheet.write(row, 6, values['purchase_total'], total_money_format)
        row += 3

        # ============================================================
        # PURCHASE TAX SUMMARY
        # ============================================================

        sheet.write(row, 0, 'Purchase Tax Summary', section_format)
        row += 1

        for col, header in enumerate(
            ['Tax Group', 'Subtotal', 'Tax', 'Total']
        ):
            sheet.write(row, col, header, header_format)
        row += 1

        for tax_group in values['purchase_tax_groups'].values():
            sheet.write(row, 0, tax_group['name'], text_format)
            sheet.write(row, 1, tax_group['subtotal'], money_format)
            sheet.write(row, 2, tax_group['tax'], money_format)
            sheet.write(row, 3, tax_group['total'], money_format)
            row += 1
