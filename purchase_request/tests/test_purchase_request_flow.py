
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'purchase_request')
class TestPurchaseRequestFlow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.vendor = cls.env['res.partner'].create({
            'name': 'Global Supplies Inc',
            'partner_code': 'VEND-TEST-001',
            'tier_level': 'gold',
            'is_credit_approved': True,
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'Industrial Laptop Stand',
            'standard_price': 50.0,
            'list_price': 80.0,
            'type': 'consu',
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'Wireless Ergonomic Mouse',
            'standard_price': 25.0,
            'list_price': 45.0,
            'type': 'consu',
        })

        # Base user (Requester)
        cls.requester_user = cls.env['res.users'].create({
            'name': 'Alice Requester',
            'login': 'alice_req',
            'email': 'alice@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('purchase_request.group_purchase_request_user').id,
            ])],
        })

        # Approver / Manager user
        cls.approver_user = cls.env['res.users'].create({
            'name': 'Bob Approver',
            'login': 'bob_app',
            'email': 'bob@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('purchase_request.group_purchase_request_manager').id,
                cls.env.ref('purchase.group_purchase_user').id,
            ])],
        })

    def test_01_requisition_creation_and_totals(self):
        """Test creating a requisition, checking automatic sequence and estimated totals."""
        req = self.env['purchase.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'partner_id': self.vendor.id,
            'assigned_approver': self.approver_user.id,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'product_qty': 10.0,
                    'estimated_cost': 50.0,
                }),
                (0, 0, {
                    'product_id': self.product_b.id,
                    'product_qty': 20.0,
                    'estimated_cost': 25.0,
                }),
            ]
        })
        self.assertNotEqual(req.name, 'New', "Sequence reference should be generated.")
        self.assertTrue(req.name.startswith('PR/'), "Sequence prefix should start with PR/")
        self.assertEqual(req.state, 'draft')
        # Total = 10 * 50 + 20 * 25 = 500 + 500 = 1000
        self.assertEqual(req.estimated_total, 1000.0, "Estimated total should match sum of line subtotals.")

    def test_02_submit_and_approve_workflow(self):
        """Test submit, access-controlled approval, and rejection."""
        # Empty request submission should fail
        empty_req = self.env['purchase.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
        })
        with self.assertRaises(UserError):
            empty_req.action_submit()

        # Valid request
        req = self.env['purchase.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.approver_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'product_qty': 5.0,
                'estimated_cost': 50.0,
            })]
        })
        req.action_submit()
        self.assertEqual(req.state, 'submitted')

        # Requester cannot approve their own request
        with self.assertRaises(UserError):
            req.with_user(self.requester_user).action_approve()

        # Approver approves
        req.with_user(self.approver_user).action_approve()
        self.assertEqual(req.state, 'approved')

        # Test rejection and reset to draft workflow on a secondary request
        req_reject = self.env['purchase.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.approver_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_b.id,
                'product_qty': 2.0,
                'estimated_cost': 25.0,
            })]
        })
        req_reject.action_submit()
        self.assertEqual(req_reject.state, 'submitted')

        # Requester cannot reject
        with self.assertRaises(UserError):
            req_reject.with_user(self.requester_user).action_reject()

        # Approver rejects
        req_reject.with_user(self.approver_user).action_reject()
        self.assertEqual(req_reject.state, 'rejected')

        # Reset to draft
        req_reject.action_reset_to_draft()
        self.assertEqual(req_reject.state, 'draft')

        # Cancel request
        req_reject.action_cancel()
        self.assertEqual(req_reject.state, 'cancel')

    def test_03_create_rfq_and_po_confirmation(self):
        """Test full end-to-end: Approved Request -> RFQ Creation -> PO Confirmation & Approval Stamp."""
        req = self.env['purchase.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.approver_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'product_qty': 4.0,
                    'estimated_cost': 50.0,
                })
            ]
        })
        req.action_submit()
        req.with_user(self.approver_user).action_approve()

        # Convert to RFQ
        action = req.with_user(self.approver_user).action_create_rfq()
        self.assertTrue(req.purchase_order_id, "Purchase Order link must be established on Request.")
        po = req.purchase_order_id

        self.assertEqual(po.partner_id.id, self.vendor.id, "PO Vendor should match request suggested vendor.")
        self.assertEqual(po.purchase_request_id.id, req.id, "PO should point back to Purchase Request.")
        self.assertEqual(len(po.order_line), 1, "PO should have 1 line item.")
        self.assertEqual(po.order_line[0].product_qty, 4.0)
        self.assertEqual(po.order_line[0].price_unit, 50.0)

        # Confirm Order
        po.with_user(self.approver_user).button_confirm()
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(po.approved_by_id.id, self.approver_user.id, "Confirming PO should stamp approved_by_id.")
        self.assertTrue(po.date_approved, "Confirming PO should stamp approval timestamp.")
        self.assertEqual(po.approval_tier, 'tier_1', "Amount < 5000 should assign Tier 1.")

    def test_04_xlsx_export_wizard(self):
        """Test the XLSX Export Wizard generates an Excel workbook."""
        # Confirm an order so SQL view has records
        req = self.env['purchase.request'].create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.approver_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'product_qty': 2.0,
                'estimated_cost': 50.0,
            })]
        })
        req.action_submit()
        req.action_approve()
        req.action_create_rfq()
        po = req.purchase_order_id
        po.button_confirm()

        wizard = self.env['purchase.approval.export.wizard'].create({
            'approval_tier': 'tier_1',
        })
        action = wizard.action_generate_xlsx()
        self.assertTrue(wizard.file_data, "Wizard should generate binary spreadsheet data.")
        self.assertTrue(wizard.filename.endswith('.xlsx'), "Filename should have .xlsx extension.")

    def test_05_security_and_reports(self):
        """Test multi-tier security record rules and QWeb report rendering."""
        charlie_user = self.env['res.users'].create({
            'name': 'Charlie Requester',
            'login': 'charlie_req',
            'email': 'charlie@example.com',
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('purchase_request.group_purchase_request_user').id,
            ])],
        })

        # Charlie creates a request
        charlie_req = self.env['purchase.request'].with_user(charlie_user).create({
            'requested_by': charlie_user.id,
            'partner_id': self.vendor.id,
            'assigned_approver': self.approver_user.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_a.id,
                'product_qty': 3.0,
                'estimated_cost': 50.0,
            })]
        })

        # Alice (Requester) should NOT see Charlie's request in search results due to personal record rule
        alice_requests = self.env['purchase.request'].with_user(self.requester_user).search([('id', '=', charlie_req.id)])
        self.assertFalse(alice_requests, "Alice should not have visibility into Charlie's personal requisition.")

        # Bob (Approver/Manager) CAN see Charlie's request
        bob_requests = self.env['purchase.request'].with_user(self.approver_user).search([('id', '=', charlie_req.id)])
        self.assertTrue(bob_requests, "Approver/Manager should have visibility into Charlie's requisition.")

        # Test QWeb PDF Reports generation
        charlie_req.action_submit()
        charlie_req.with_user(self.approver_user).action_approve()
        charlie_req.with_user(self.approver_user).action_create_rfq()
        po = charlie_req.purchase_order_id
        po.with_user(self.approver_user).button_confirm()

        # Render Purchase Requisition Slip (QWeb HTML content)
        html_content, _ = self.env['ir.actions.report']._render_qweb_html(
            'purchase_request.action_report_purchase_request',
            charlie_req.ids
        )
        self.assertIn(charlie_req.name, html_content.decode('utf-8'), "PR report should contain requisition sequence.")
        self.assertIn('Charlie Requester', html_content.decode('utf-8'), "PR report should contain requester name.")

        # Render PO Approval Certificate (QWeb HTML content)
        html_po_content, _ = self.env['ir.actions.report']._render_qweb_html(
            'purchase_request.action_report_purchase_order_approval',
            po.ids
        )
        self.assertIn(po.name, html_po_content.decode('utf-8'), "PO approval report should contain PO name.")
        self.assertIn('Bob Approver', html_po_content.decode('utf-8'), "PO approval report should contain approver name.")
