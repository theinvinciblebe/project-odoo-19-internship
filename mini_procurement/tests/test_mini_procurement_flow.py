from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install', 'mini_procurement')
class TestMiniProcurementFlow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.vendor = cls.env['res.partner'].create({
            'name': 'TechLogistics Supplies Inc',
            'partner_code': 'VEND-PROC-001',
            'tier_level': 'gold',
            'is_credit_approved': True,
        })

        cls.product_laptop = cls.env['product.product'].create({
            'name': 'Business Laptop Pro',
            'standard_price': 800.0,
            'list_price': 1200.0,
            'type': 'consu',
        })

        cls.product_dock = cls.env['product.product'].create({
            'name': 'Thunderbolt Docking Station',
            'standard_price': 150.0,
            'list_price': 250.0,
            'type': 'consu',
        })

        # Standard Procurement User (Requester)
        cls.requester_user = cls.env['res.users'].create({
            'name': 'David Requester',
            'login': 'david_req',
            'email': 'david@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('mini_procurement.group_procurement_user').id,
            ])],
        })

        # Procurement Manager (Approver)
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Emma Procurement Manager',
            'login': 'emma_mgr',
            'email': 'emma@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('mini_procurement.group_procurement_manager').id,
                cls.env.ref('purchase.group_purchase_user').id,
            ])],
        })

    def test_01_requisition_creation_and_calculations(self):
        """Test creating procurement request, checking sequence and estimated total."""
        req = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'partner_id': self.vendor.id,
            'assigned_approver': self.manager_user.id,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product_laptop.id,
                    'name': 'Business Laptop Pro',
                    'product_qty': 3.0,
                    'estimated_cost': 800.0,
                }),
                (0, 0, {
                    'product_id': self.product_dock.id,
                    'name': 'Thunderbolt Docking Station',
                    'product_qty': 3.0,
                    'estimated_cost': 150.0,
                }),
            ]
        })
        self.assertNotEqual(req.name, 'New', "Sequence reference should be generated.")
        self.assertTrue(req.name.startswith('PR/'), "Sequence prefix should start with PR/")
        self.assertEqual(req.state, 'draft')
        # Total = (3 * 800) + (3 * 150) = 2400 + 450 = 2850
        self.assertEqual(req.estimated_total, 2850.0, "Estimated total should match sum of subtotals.")

        # Test line validation constraint
        with self.assertRaises(ValidationError):
            self.env['procurement.request.line'].create({
                'request_id': req.id,
                'product_id': self.product_dock.id,
                'name': 'Invalid Line',
                'product_qty': -1.0,
                'estimated_cost': 50.0,
            })

    def test_02_workflow_state_transitions(self):
        """Test draft -> submitted -> approved -> rejected -> reset to draft -> cancel."""
        # Empty submission rejection
        empty_req = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
        })
        with self.assertRaises(UserError):
            empty_req.action_submit()

        # Valid submission
        req = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.manager_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_laptop.id,
                'name': 'Business Laptop Pro',
                'product_qty': 2.0,
                'estimated_cost': 800.0,
            })]
        })
        req.action_submit()
        self.assertEqual(req.state, 'submitted')

        # Requester cannot approve
        with self.assertRaises(UserError):
            req.with_user(self.requester_user).action_approve()

        # Manager approves
        req.with_user(self.manager_user).action_approve()
        self.assertEqual(req.state, 'approved')

        # Secondary request for rejection test
        req2 = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.manager_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_dock.id,
                'name': 'Docking Station',
                'product_qty': 1.0,
                'estimated_cost': 150.0,
            })]
        })
        req2.action_submit()
        req2.with_user(self.manager_user).action_reject(reason="Exceeds current department budget.")
        self.assertEqual(req2.state, 'rejected')
        self.assertEqual(req2.rejection_reason, "Exceeds current department budget.")

        # Reset to draft
        req2.action_reset_to_draft()
        self.assertEqual(req2.state, 'draft')

        # Cancel
        req2.action_cancel()
        self.assertEqual(req2.state, 'cancel')

    def test_03_create_rfq_and_po_tiered_approval(self):
        """Test converting approved request to PO, line transfer, and confirmation tier evaluation."""
        req = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.manager_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_laptop.id,
                'name': 'Business Laptop Pro',
                'product_qty': 5.0,
                'estimated_cost': 800.0,
            })]
        })
        req.action_submit()
        req.with_user(self.manager_user).action_approve()

        # Create RFQ
        action = req.with_user(self.manager_user).action_create_rfq()
        self.assertTrue(req.purchase_order_id, "Purchase Order reference should be linked.")
        po = req.purchase_order_id

        self.assertEqual(po.partner_id.id, self.vendor.id)
        self.assertEqual(po.procurement_request_id.id, req.id)
        self.assertEqual(len(po.order_line), 1)
        self.assertEqual(po.order_line[0].product_qty, 5.0)
        self.assertEqual(po.order_line[0].price_unit, 800.0)

        # Confirm PO and verify tier assignment
        # Total = 5 * 800 = 4000 (< $5,000 => Tier 1)
        po.with_user(self.manager_user).button_confirm()
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(po.approved_by_id.id, self.manager_user.id)
        self.assertTrue(po.date_approved)
        self.assertEqual(po.approval_tier, 'tier_1')

    def test_04_security_record_rules(self):
        """Test multi-tier record rule isolation: users cannot see other users' requisitions."""
        other_user = self.env['res.users'].create({
            'name': 'Frank Requester',
            'login': 'frank_req',
            'email': 'frank@example.com',
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('mini_procurement.group_procurement_user').id,
            ])],
        })

        frank_req = self.env['procurement.request'].with_user(other_user).create({
            'requested_by': other_user.id,
            'assigned_approver': self.manager_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_dock.id,
                'name': 'Frank dock',
                'product_qty': 1.0,
                'estimated_cost': 150.0,
            })]
        })

        # David (requester) cannot see Frank's requisition
        david_search = self.env['procurement.request'].with_user(self.requester_user).search([('id', '=', frank_req.id)])
        self.assertFalse(david_search, "David should not have visibility into Frank's personal requisition.")

        # Emma (manager) can see Frank's requisition
        emma_search = self.env['procurement.request'].with_user(self.manager_user).search([('id', '=', frank_req.id)])
        self.assertTrue(emma_search, "Manager should have full organizational visibility.")

    def test_05_reports_and_export_wizard(self):
        """Test QWeb PDF rendering and XLSX export wizard."""
        req = self.env['procurement.request'].with_user(self.requester_user).create({
            'requested_by': self.requester_user.id,
            'assigned_approver': self.manager_user.id,
            'partner_id': self.vendor.id,
            'line_ids': [(0, 0, {
                'product_id': self.product_laptop.id,
                'name': 'Business Laptop Pro',
                'product_qty': 2.0,
                'estimated_cost': 800.0,
            })]
        })
        req.action_submit()
        req.with_user(self.manager_user).action_approve()
        req.with_user(self.manager_user).action_create_rfq()
        po = req.purchase_order_id
        po.with_user(self.manager_user).button_confirm()

        # Render QWeb HTML for Requisition Slip
        html_req, _ = self.env['ir.actions.report']._render_qweb_html(
            'mini_procurement.action_report_procurement_request',
            req.ids
        )
        self.assertIn(req.name, html_req.decode('utf-8'))
        self.assertIn('David Requester', html_req.decode('utf-8'))

        # Render QWeb HTML for PO Approval Certificate
        html_po, _ = self.env['ir.actions.report']._render_qweb_html(
            'mini_procurement.action_report_procurement_order_approval',
            po.ids
        )
        self.assertIn(po.name, html_po.decode('utf-8'))
        self.assertIn('Emma Procurement Manager', html_po.decode('utf-8'))

        # Test XLSX Export Wizard
        wizard = self.env['procurement.approval.export.wizard'].create({
            'state': 'approved',
        })
        wizard.action_generate_xlsx()
        self.assertTrue(wizard.file_data, "Binary excel data should be generated.")
        self.assertTrue(wizard.filename.endswith('.xlsx'), "Generated filename should have .xlsx extension.")
