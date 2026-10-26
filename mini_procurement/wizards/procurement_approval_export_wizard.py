import base64
import io
from odoo import fields, models, _
import xlsxwriter


class ProcurementApprovalExportWizard(models.TransientModel):
    _name = 'procurement.approval.export.wizard'
    _description = 'Procurement Approval XLSX Export Wizard'

    date_from = fields.Date(string='From Request Date')
    date_to = fields.Date(string='To Request Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Filter Status')
    assigned_approver = fields.Many2one(
        'res.users', string='Filter by Approver'
    )

    file_data = fields.Binary(string='Download File', readonly=True)
    filename = fields.Char(string='Filename', readonly=True)

    def action_generate_xlsx(self):
        """Query SQL view data, format spreadsheet, and return download dialog."""
        domain = []
        if self.date_from:
            domain.append(('date_request', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_request', '<=', self.date_to))
        if self.state:
            domain.append(('state', '=', self.state))
        if self.assigned_approver:
            domain.append(('assigned_approver', '=', self.assigned_approver.id))

        records = self.env['procurement.approval.report'].search(
            domain, order='date_request desc'
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Procurement Analysis')
        sheet.set_paper(9)  # A4

        # Styling
        title_fmt = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': '#1B365D',
            'align': 'left',
            'valign': 'vcenter',
        })
        subtitle_fmt = workbook.add_format({
            'italic': True,
            'font_size': 9,
            'font_color': '#6C757D',
        })
        header_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': '#FFFFFF',
            'bg_color': '#1B365D',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        cell_text = workbook.add_format({
            'font_size': 9,
            'align': 'left',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E9ECEF',
        })
        cell_center = workbook.add_format({
            'font_size': 9,
            'align': 'center',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E9ECEF',
        })
        cell_currency = workbook.add_format({
            'font_size': 9,
            'num_format': '$#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'bottom': 1,
            'border_color': '#E9ECEF',
        })
        total_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'num_format': '$#,##0.00',
            'align': 'right',
            'top': 2,
            'bottom': 6,
            'bg_color': '#F8F9FA',
        })
        total_label_fmt = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'top': 2,
            'bottom': 6,
            'bg_color': '#F8F9FA',
        })

        # Title & Subtitle
        sheet.merge_range('A1:H1', 'Mini Procurement Summary & Audit Report', title_fmt)
        sheet.write('A2', f'Generated on: {fields.Datetime.now().strftime("%Y-%m-%d %H:%M")} (UTC)', subtitle_fmt)

        headers = [
            ('Reference', 16),
            ('Date', 13),
            ('Requested By', 20),
            ('Approver', 20),
            ('Vendor', 26),
            ('Status', 14),
            ('PO Ref', 15),
            ('Estimated Total', 18),
        ]

        row = 3
        for col_idx, (header_text, col_width) in enumerate(headers):
            sheet.write(row, col_idx, header_text, header_fmt)
            sheet.set_column(col_idx, col_idx, col_width)
        sheet.set_row(row, 24)

        start_data_row = row + 1
        current_row = start_data_row

        for rec in records:
            sheet.write(current_row, 0, rec.name or '', cell_center)
            sheet.write(
                current_row, 1,
                rec.date_request.strftime('%Y-%m-%d') if rec.date_request else '',
                cell_center
            )
            sheet.write(current_row, 2, rec.requested_by.name or '', cell_text)
            sheet.write(current_row, 3, rec.assigned_approver.name or '', cell_text)
            sheet.write(current_row, 4, rec.partner_id.name or '', cell_text)
            sheet.write(current_row, 5, (rec.state or '').capitalize(), cell_center)
            sheet.write(current_row, 6, rec.purchase_order_id.name or '-', cell_center)
            sheet.write(current_row, 7, rec.estimated_total or 0.0, cell_currency)
            current_row += 1

        if current_row > start_data_row:
            sheet.merge_range(current_row, 0, current_row, 6, 'Total Estimated Outlay:', total_label_fmt)
            formula = f'=SUM(H{start_data_row + 1}:H{current_row})'
            sheet.write_formula(current_row, 7, formula, total_fmt)
        else:
            sheet.write(current_row, 0, 'No procurement records match criteria.', subtitle_fmt)

        workbook.close()
        output.seek(0)

        self.write({
            'file_data': base64.b64encode(output.read()),
            'filename': f'Procurement_Report_{fields.Date.today()}.xlsx',
        })
        output.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
