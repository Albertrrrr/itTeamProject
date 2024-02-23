from django.db import models
from eShop.models import CustomUser

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

