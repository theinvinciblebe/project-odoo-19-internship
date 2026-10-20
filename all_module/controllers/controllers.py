# from odoo import http


# class W3Module(http.Controller):
#     @http.route('/all_module/all_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/all_module/all_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('all_module.listing', {
#             'root': '/all_module/all_module',
#             'objects': http.request.env['all_module.all_module'].search([]),
#         })

#     @http.route('/all_module/all_module/objects/<model("all_module.all_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('all_module.object', {
#             'object': obj
#         })

