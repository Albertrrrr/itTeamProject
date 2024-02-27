import json

from celery import shared_task
from alipay import AliPay
import time

from django.db.models import F

from backstage.models import Order, Product

app_private_key_string = open("backstage/Privatekey.txt").read()
alipay_public_key_string = open("backstage/alipayPublicCert.txt").read()


@shared_task
def query_order_status(order_id):
    alipay = AliPay(
        appid="9021000129661967",
        app_notify_url=None,  # 异步通知URL，本例中不使用
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=True  # 根据是否是沙箱环境设置
    )
    flag = False
    order = Order.objects.get(id=order_id)
    for _ in range(180):
        response = alipay.api_alipay_trade_query(out_trade_no=order_id)
        if response.get("trade_status", "") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            print("支付成功")
            # 更新数据库中的订单状态为已支付
            try:
                order.isPaid = True
                data = order.item
                print(f"订单{order_id}的支付状态已更新为已支付。")
                flag = True
                if flag:
                    order.status = "processing"
                    for item in data:
                        product_id = item["productID"]
                        quantity = item["quantity"]

                        # 尝试获取Product实例，然后更新库存
                        try:
                            product = Product.objects.get(pk=product_id)
                            product.stock -= quantity  # 假设您是减去库存
                            product.save()
                            print(f"Updated stock for Product ID {product_id}. New stock is {product.stock}.")
                        except Product.DoesNotExist:
                            print(f"Product with ID {product_id} does not exist.")

                else:
                    order.status = "cancel"
                order.save()
                break
            except Order.DoesNotExist:
                break
        time.sleep(5)



