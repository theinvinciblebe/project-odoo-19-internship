import base64
import io
from odoo import fields, models
import xlsxwriter


class PurchaseApprovalExportWizard(models.TransientModel):
    _name = 'purchase.approval.export.wizard'
    _description = 'Purchase Approval XLSX Export Wizard'

    date_from = fields.Datetime(string='From Approval Date')
    date_to = fields.Datetime(string='To Approval Date')
    approval_tier = fields.Selection(
        [
            ('tier_1', 'Tier 1 (Standard Manager)'),
            ('tier_2', 'Tier 2 (Finance Director)'),
            ('tier_3', 'Tier 3 (Executive Board)'),
        ],
        string='Filter Approval Tier',
    )
    approved_by_id = fields.Many2one(
        'res.users', string='Filter by Approver'
    )

    file_data = fields.Binary(string='Download File', readonly=True)
    filename = fields.Char(string='Filename', readonly=True)

    def action_generate_xlsx(self):
        """Query SQL view data, format spreadsheet, and return download dialog."""
        # 1. Build Domain Filters
        domain = []
        if self.date_from:
            domain.append(('date_approved', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_approved', '<=', self.date_to))
        if self.approval_tier:
            domain.append(('approval_tier', '=', self.approval_tier))
        if self.approved_by_id:
            domain.append(('approved_by_id', '=', self.approved_by_id.id))

        records = self.env['purchase.approval.report'].search(
            domain, order='date_approved desc'
        )

        # 2. Initialize in-memory Excel Workbook
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Approval Audit Summary')
        sheet.set_paper(9)  # A4 size

        # 3. Define Clean Styling Palettes
        title_fmt = workbook.add_format({
            'bold': True,
            'font_size': 15,
            'font_color': '#2C3E50',
            'align': 'left',
            'valign': 'vcenter',
        })
        subtitle_fmt = workbook.add_format({
            'italic': True,
            'font_size': 9,
            'font_color': '#7F8C8D',
        })
        header_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': '#FFFFFF',
            'bg_color': '#2C3E50',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        cell_text = workbook.add_format({
            'font_size': 9,
            'align': 'left',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E0E0E0',
        })
        cell_center = workbook.add_format({
            'font_size': 9,
            'align': 'center',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E0E0E0',
        })
        cell_currency = workbook.add_format({
            'font_size': 9,
            'num_format': '$#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E0E0E0',
        })
        total_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'num_format': '$#,##0.00',
            'align': 'right',
            'top': 2,
            'bottom': 6,
            'bg_color': '#ECF0F1',
        })
        total_label_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'top': 2,
            'bottom': 6,
            'bg_color': '#ECF0F1',
        })

        # 4. Sheet Header & Metadata
        sheet.merge_range('A1:H1', 'Purchase Approval Audit & Analytics Report', title_fmt)
        sheet.write('A2', f'Generated on: {fields.Datetime.now().strftime("%Y-%m-%d %H:%M")} (UTC)', subtitle_fmt)

        # 5. Table Columns Header Row
        headers = [
            ('PO Number', 15),
            ('Vendor', 28),
            ('Partner Tier', 14),
            ('Credit Status', 14),
            ('Approval Tier', 20),
            ('Approved By', 20),
            ('Approval Date', 18),
            ('Total Amount', 16),
        ]

        row = 3
        for col_idx, (header_text, col_width) in enumerate(headers):
            sheet.write(row, col_idx, header_text, header_fmt)
            sheet.set_column(col_idx, col_idx, col_width)

        sheet.set_row(row, 24)

        # 6. Populate Rows
        start_data_row = row + 1
        current_row = start_data_row

        for rec in records:
            sheet.write(current_row, 0, rec.purchase_order_id.name or '', cell_center)
            sheet.write(current_row, 1, rec.partner_id.name or '', cell_text)
            sheet.write(current_row, 2, (rec.partner_tier or '').upper(), cell_center)
            sheet.write(
                current_row,
                3,
                'Approved' if rec.is_credit_approved else 'Pending',
                cell_center,
            )
            sheet.write(current_row, 4, rec.approval_tier or '', cell_center)
            sheet.write(current_row, 5, rec.approved_by_id.name or '', cell_text)
            sheet.write(
                current_row,
                6,
                rec.date_approved.strftime('%Y-%m-%d %H:%M') if rec.date_approved else '',
                cell_center,
            )
            sheet.write(current_row, 7, rec.amount_total or 0.0, cell_currency)
            current_row += 1

        # 7. Summary Total Row with Formulas
        if current_row > start_data_row:
            sheet.merge_range(current_row, 0, current_row, 6, 'Total Approved Outlay:', total_label_fmt)
            formula = f'=SUM(H{start_data_row + 1}:H{current_row})'
            sheet.write_formula(current_row, 7, formula, total_fmt)
        else:
            sheet.write(current_row, 0, 'No approval records found for selected filters.', subtitle_fmt)

        workbook.close()
        output.seek(0)

        # 8. Store and Return File
        self.write({
            'file_data': base64.b64encode(output.read()),
            'filename': f'Approval_Audit_Report_{fields.Date.today()}.xlsx',
        })
        output.close()

        # Reopen same wizard view showing the ready download button
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }