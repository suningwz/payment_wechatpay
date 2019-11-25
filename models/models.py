# -*- coding: utf-8 -*-

from odoo import models, fields, api
from wechatpy.pay import WeChatPay
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AcquirerWeChatPay(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[('wechatpay', 'WeChatPay')])
    wechatpay_appid = fields.Char("WeChatPay AppId", size=32)
    wechatpay_app_key = fields.Char("Api Key")
    wechatpay_mch_id = fields.Char("Merchant Id", size=32)
    wechatpay_mch_key = fields.Binary("Merchat Key")
    wechatpay_mch_cert = fields.Binary("Merchant Cert")

    def _get_feature_support(self):
        res = super(AcquirerWeChatPay, self)._get_feature_support()
        res['fees'].append('wechatpay')
        return res

    def _get_wechatpay(self):
        """获取微信支付客户端"""
        try:
            # WeChatPay has no sandbox enviroment.
            wechatpay = WeChatPay(self.wechatpay_appid,
                                  self.wechatpay_app_key,
                                  self.wechatpay_mch_id,
                                  mch_cert=self.wechatpay_mch_cert,
                                  mch_key=self.wechatpay_mch_key)
            return wechatpay
        except Exception as err:
            _logger.exception(f"生成微信支付客户端失败:{err}")

    def _get_qrcode_url(self, order):
        """获取微信支付二维码"""
        wechatpay = self._get_wechatpay()
        wechatpay.order.create(trade_type="NATIVE", body=order.name,
                               out_trade_no=order.name, total_fee="1", notify_url="")
        # [FIXME] 伪代码
        qrstring = "weixin://wxpay/s/An4baqw"
        return qrstring

    @api.multi
    def wechatpay_get_form_action_url(self):
        """统一下单"""
        return "/shop/wechatpay"

    @api.multi
    def wechatpay_from_generate_values(self, values):
        wechatpay_tx_values = dict(values)
        return wechatpay_tx_values

    def _verify_wechatpay(self, data):
        """验证微信支付服务器返回的信息"""
        # [FIXME]
        # 校验支付信息
        transaction = self.env["payment.transaction"].sudo().search(
            [('reference', '=', data["out_trade_no"])], limit=1)
        # 将支付结果设置完成
        transaction._set_transaction_done()
        return True


class TxWeChatpay(models.Model):
    _inherit = "payment.transaction"

    wechatpay_txn_type = fields.Char('Transaction type')

    @api.model
    def _wechatpay_form_get_tx_from_data(self, data):
        """获取支付事务"""
        if not data.get("out_trade_no", None):
            raise ValidationError("订单号错误")
        reference = data.get("out_trade_no")
        txs = self.env["payment.transaction"].search(
            [('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'WeChatPay: received data for reference %s' % (
                reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _wechatpay_form_validate(self, data):
        """验证微信支付"""
        if self.state == 'done':
            _logger.info(f"支付已经验证：{data['out_trade_no']}")
            return True
        result = {
            "acquirer_reference": data["trade_no"]
        }
        # 根据支付宝同步返回的信息，去支付宝服务器查询
        payment = self.env["payment.acquirer"].sudo().search(
            [('provider', '=', 'wechatpay')], limit=1)
        wechatpay = payment._get_wechatpay()
        # [FIXME] 去微信服务器验证支付结果
        self._set_transaction_done()
        return self.write(result)
