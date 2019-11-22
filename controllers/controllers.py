# -*- coding: utf-8 -*-
from odoo import http

# class PaymentWechat(http.Controller):
#     @http.route('/payment_wechat/payment_wechat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_wechat/payment_wechat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_wechat.listing', {
#             'root': '/payment_wechat/payment_wechat',
#             'objects': http.request.env['payment_wechat.payment_wechat'].search([]),
#         })

#     @http.route('/payment_wechat/payment_wechat/objects/<model("payment_wechat.payment_wechat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_wechat.object', {
#             'object': obj
#         })