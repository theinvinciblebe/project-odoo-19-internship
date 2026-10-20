# from odoo import http


# class CustomBusinessFields(http.Controller):
#     @http.route('/custom_business_fields/custom_business_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_business_fields/custom_business_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_business_fields.listing', {
#             'root': '/custom_business_fields/custom_business_fields',
#             'objects': http.request.env['custom_business_fields.custom_business_fields'].search([]),
#         })

#     @http.route('/custom_business_fields/custom_business_fields/objects/<model("custom_business_fields.custom_business_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_business_fields.object', {
#             'object': obj
#         })

