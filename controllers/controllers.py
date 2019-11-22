# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, redirect_with_hash
import logging
import qrcode
from io import BytesIO
import base64
import json
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WeChatPay(http.Controller):

    def make_qrcode(self, qrurl):
        """根据URL生成二维码字符"""
        img = qrcode.make(qrurl)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        heximage = base64.b64encode(buffer.getvalue())
        return "data:image/png;base64,{}".format(heximage.decode('utf-8'))

    @http.route('/shop/wechatpay', type='http', auth="public", website=True)
    def index(self, **kw):
        order = request.website.sale_get_order()
        # 获取微信支付
        acquirer = request.env['payment.acquirer'].sudo().search(
            [('provider', '=', 'wechatpay')], limit=1)
        qrcode = acquirer._get_qrcode_url()
        values = {}
        values['qrcode'] = self.make_qrcode(qrcode)
        values['order'] = order.name
        values['amount'] = order.amount_total

        return request.render("payment_wechatpay.wechatpay_pay", values)

    @http.route('/shop/wechatpay/result', type='http', auth="public", website=True)
    def wechatpay_query(self):
        """轮询支付结果"""
        # [FIXME] 根据微信支付返回结果
        return json.dumps({"result": 0})

    def validate_pay_data(self, **kwargs):
        res = request.env['payment.transaction'].sudo(
        ).form_feedback(kwargs, 'wechatpay')
        return res

    @http.route('/payment/wechatpay/validate', type="http", auth="none", methods=['POST', 'GET'], csrf=False)
    def wechatpay_validate(self, **kwargs):
        """页面跳转后验证支付结果"""
        _logger.info("开始验证微信支付结果...")
        try:
            # [FIXME] 验证微信支付结果
            kwargs['out_trade_no'] = 'SO823-37'
            kwargs['trade_no'] = 'xxxxxxx'
            res = self.validate_pay_data(**kwargs)
        except ValidationError:
            _logger.exception("支付验证失败")
        return redirect_with_hash("/payment/process")

    @http.route('/payment/wechatpay/notify', csrf=False, type="http", auth='none', method=["POST"])
    def alipay_notify(self, **kwargs):
        """接收微信支付异步通知"""
        _logger.debug(f"接收微信支付异步通知...收到的数据:{kwargs}")
        payment = request.env["payment.acquirer"].sudo().search(
            [('provider', '=', 'wechatpay')], limit=1)
        result = payment._verify_wechatpay(kwargs)
        return "success" if result else "failed"
