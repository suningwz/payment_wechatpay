
function wechatpay_query() {
    $(document).ready(function () {
        $.ajax({
            type: "GET",
            url: "/shop/wechatpay/result",
            dataType: "json",
            success: function (res) {
                if (res.result == 0) {
                    //跳转后续页面
                    window.location.href = '/payment/wechatpay/validate'
                }
            }
        });
    });
}
setInterval('wechatpay_query()', 2000);