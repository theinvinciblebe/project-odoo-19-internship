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