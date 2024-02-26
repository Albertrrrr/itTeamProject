from django.db import models, transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from eShop.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class productCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()  # 使用 TextField 对应 VARCHAR(255) 是合适的，它没有长度限制

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    categoryID = models.ForeignKey('productCategory', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.FloatField(10)
    stock = models.IntegerField(10)
    description = models.TextField(null=True)
    url = models.TextField(null=True)

    def __str__(self):
        return self.name

class ShoppingCart(models.Model):
    userID = models.OneToOneField('eShop.CustomUser', on_delete=models.CASCADE)


class ShoppingCartItem(models.Model):
    cartID = models.ForeignKey('ShoppingCart',on_delete=models.DO_NOTHING)
    productID = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)

    def clean(self):
        # 获取产品的库存量
        product_stock = self.productID.stock
        # 验证数量是否超过库存量
        if self.quantity > product_stock:
            raise ValidationError(
                {'quantity': f'Quantity cannot exceed the stock available. Stock available: {product_stock}.'})
        # 验证数量是否低于最小值
        if self.quantity < 1:
            raise ValidationError({'quantity': 'Quantity cannot be less than 1.'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 检查库存是否足够
            if self.productID.stock < self.quantity:
                raise ValidationError('The quantity exceeds the available stock.')

            existing_item = ShoppingCartItem.objects.filter(cartID=self.cartID, productID=self.productID).exclude(
                pk=self.pk).first()

            if existing_item:
                # 如果存在相同的项，更新该项的数量并减少库存
                new_quantity = existing_item.quantity + self.quantity

                if new_quantity > self.productID.stock :
                    raise ValidationError('The quantity exceeds the available stock after update.')
                ShoppingCartItem.objects.filter(pk=existing_item.pk).update(quantity=F('quantity') + self.quantity)
                # 减少库存
                # 重新从数据库加载productID以获取更新后的库存
                self.productID.refresh_from_db()
            else:
                # 减少库存并保存新的购物车项
                super().save(*args, **kwargs)


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    house_number_and_street = models.CharField(max_length=255, verbose_name='House Number and Street')
    area = models.CharField(max_length=255, blank=True, null=True, verbose_name='Area')
    town = models.CharField(max_length=255, verbose_name='Town')
    county = models.CharField(max_length=255, blank=True, null=True, verbose_name='County')
    postcode = models.CharField(max_length=8, verbose_name='Postcode')
    country = models.CharField(max_length=255, default='United Kingdom', verbose_name='Country')

    def __str__(self):
        return f"{self.house_number_and_street}, {self.town}, {self.postcode}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

class Order(models.Model):
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('cancel', 'Cancel'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('done', 'Done'),
    )
    IS_PAID_CHOICES = (
        (True, 'Paid'),
        (False, 'Not Paid'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    item = models.JSONField(default=dict)
    address = models.JSONField(default=dict, verbose_name="Address")
    totalCost = models.FloatField(10)
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    finishTime = models.DateTimeField(blank=True, null=True, verbose_name="Finish Time")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid', verbose_name="Status")
    isPaid = models.BooleanField(choices=IS_PAID_CHOICES, default=False, verbose_name="Is Paid")


    def __str__(self):
        return f"Order {self.id} - Status: {self.get_status_display()}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

