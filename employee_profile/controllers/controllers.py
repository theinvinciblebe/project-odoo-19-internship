# from odoo import http


# class EmployeeProfile(http.Controller):
#     @http.route('/employee_profile/employee_profile', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_profile/employee_profile/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_profile.listing', {
#             'root': '/employee_profile/employee_profile',
#             'objects': http.request.env['employee_profile.employee_profile'].search([]),
#         })

#     @http.route('/employee_profile/employee_profile/objects/<model("employee_profile.employee_profile"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_profile.object', {
#             'object': obj
#         })

