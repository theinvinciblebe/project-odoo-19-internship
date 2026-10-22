# Task Tracker (`w3_module`) — Compact Reference

### 🟢 Week 2: ORM & Models (`models/models.py`)
- **Core Types**: `name` (Char), `is_urgent` (Boolean), `date_deadline` (Date), `start_datetime` (Datetime), `priority` (Selection), `state` (Selection), `description` (Html).
- **Relations**: `user_id` (Many2one), `tag_ids` (Many2many), `subtask_ids` (One2many).
- **Computed Fields**:
  - `total_actual_hours` (`store=True`): Sums `subtask_ids.actual_hours`.
  - `is_overdue` (`store=False`): Dynamic check against `date.today()`.

### 🟢 Week 3: Views & UI (`views/views.xml`)
- **List / Tree View**: `decoration-*`, `default_order`, `optional` columns.
- **Form View**: Statusbar, 2-column groups, `<notebook>` tabs (`Subtasks`, `Description`).
- **Kanban View**: Grouped by `state`, `quick_create="true"`, card templates.
- **Search View**: Filters (`My Tasks`, `Urgent`, `Overdue`) & Group By (`Assignee`, `Status`, `Deadline`).

### 🟢 Week 4: Security (`security/`)
- **`res.groups`** (`security.xml`): `group_task_user`, `group_task_manager`.
- **`ir.model.access.csv`**: CRUD rights for User & Manager.
- **`ir.rule`** (`security.xml`): User personal filter & Manager full access.

### 🟢 Week 5: Workflow & Email Notifications (`purchase_request`)
- **Trigger**: Automated notification sent upon state change to `approved`.
- **Mail Template**: `mail.template` defined in `data/purchase_request_data.xml`.
- **Dispatch**: `template.send_mail(...)` executed within `action_approve()`.

### 🟢 Week 6: Business Field Extensions & Form Injection (`purchase_request`)
- **`res.partner`**: Added `partner_code` (Char), `tier_level` (Selection), and `is_credit_approved` (Boolean).
- **`purchase.order`**: Added approval audit fields (`approved_by_id`, `date_approved`, `approval_notes`, `approval_tier`).
- **XPath Injection**: Injected custom approval panel directly above notebook tabs in standard PO form (`purchase.purchase_order_form`).

### 🟢 Week 7: Reports, SQL Views & XLSX Export (`purchase_request`)
- **QWeb PDF Report**: `ir.actions.report` with `qweb-pdf` generating Approval Audit Certificate.
- **SQL View Model**: `purchase.approval.report` (`_auto = False`) aggregating PO spend by approver, tier, and credit approval.
- **Analytics Views**: Interactive Pivot table and stacked Bar Graph views.
- **XLSX Export Wizard**: Transient wizard utilizing `xlsxwriter` for customized Excel audit downloads.

### 🟢 Week 8: Native Purchase & Inventory Flow (`purchase_request/PURCHASE_INVENTORY_FLOW.md`)
- **RFQ (`draft`/`sent`)**: Price negotiation, sequence generation, email dispatch via `action_rfq_send()`.
- **PO (`purchase`)**: Binding contract, triggers `_create_picking()`, stamps approval credentials.
- **Receipt (`stock.picking`)**: Inbound shipment validation (`button_validate()`), automated stock valuation (Interim Received / WH Stock), and backorder management.
- **Vendor Bill (`account.move`)**: 3-way matching (`ordered` vs `received` vs `billed`), interim clearing reconciliation, and payment registration (`account.payment`).