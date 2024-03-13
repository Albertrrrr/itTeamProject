import json

from celery import shared_task
from alipay import AliPay
import time,os

from django.db.models import F

from backstage.models import Order, Product
# Get the absolute path to the current working directory
current_working_directory = os.getcwd()

# Absolute path to build to a specific file
app_private_key_path = os.path.join(current_working_directory, 'backstage', 'PrivateKey.txt')
alipay_public_key_path = os.path.join(current_working_directory, 'backstage', 'alipayPublicCert.txt')

# Open and read files securely using the with statement
with open(app_private_key_path, 'r') as file:
     app_private_key_string = file.read()

with open(alipay_public_key_path, 'r') as file:
    alipay_public_key_string = file.read()


@shared_task
def query_order_status(order_id):
    alipay = AliPay(
        appid="9021000129661967",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=True
    )
    flag = False
    order = Order.objects.get(id=order_id)
    for _ in range(180):
        response = alipay.api_alipay_trade_query(out_trade_no=order_id)
        if response.get("trade_status", "") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            print("Payment successful")
            try:
                order.isPaid = True
                data = order.item
                print(f"Order{order_id}:The payment status has been updated to Paid。")
                flag = True
                if flag:
                    order.status = "processing"
                    for item in data:
                        product_id = item["productID"]
                        quantity = item["quantity"]

                        try:
                            product = Product.objects.get(pk=product_id)
                            product.stock -= quantity
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



