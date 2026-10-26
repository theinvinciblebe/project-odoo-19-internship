# Odoo 19 Internship Modules

This repository contains custom Odoo 19 modules developed during the internship project.

## Modules Overview

| Module | Summary | Dependencies |
| **`mini_procurement`** | End-to-end Mini Procurement workflow: Requisitions, Tiered Approvals, Vendor Intelligence, PO Generation, QWeb PDF Reports, SQL Analytics & XLSX Exports. | `base`, `mail`, `purchase` |
| **`purchase_request`** | End-to-end mini procurement workflow: Requisitions, Tiered Approvals, Vendor Intelligence, PO Generation, Audit Reports & Excel Exports. | `base`, `mail`, `purchase` |
| **`school_management`** | School management system handling Students, Classrooms, and Subjects. | `base` |
| **`custom_business_fields`** | Custom business field extensions on Contacts (`res.partner`) and Purchase Orders (`purchase.order`). | `base`, `contacts`, `purchase` |
| **`all_module`** | Task tracker and weekly task implementation management. | `base` |
| **`student_module`** | Student records with chatter / mail tracking support. | `base`, `mail` |
| **`first_module`** | Introductory practice module with custom views and chatter. | `base`, `mail` |

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theinvinciblebe/project-odoo-19-internship.git custom
   ```

2. **Add to Odoo Configuration (`odoo.conf`):**
   Add the path to this `custom` directory into your `addons_path`:
   ```ini
   addons_path = /path/to/odoo/addons,/path/to/custom
   ```

3. **Update Apps List:**
   - Restart the Odoo server.
   - Activate **Developer Mode** in the Odoo web interface.
   - Go to **Apps** &rarr; **Update Apps List**.
   - Search for and install the desired modules.
