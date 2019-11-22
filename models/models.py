# -*- coding: utf-8 -*-

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AcquirerWechatPay(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[('wechatpay', 'WechatPay')])
    wechatpay_appid = fields.Char("WechatPay AppId", size=32)
    wechatpay_mch_id = fields.Char("Merchant Id", size=32)

    def _get_feature_support(self):
        res = super(AcquirerWechatPay, self)._get_feature_support()
        res['fees'].append('wechatpay')
        return res
