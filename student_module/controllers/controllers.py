# from odoo import http


# class StudentModule(http.Controller):
#     @http.route('/student_module/student_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/student_module/student_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('student_module.listing', {
#             'root': '/student_module/student_module',
#             'objects': http.request.env['student_module.student_module'].search([]),
#         })

#     @http.route('/student_module/student_module/objects/<model("student_module.student_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('student_module.object', {
#             'object': obj
#         })

