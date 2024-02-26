from rest_framework import serializers
from .models import productCategory, Product, ShoppingCartItem


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = productCategory
        fields = '__all__'  # 列出所有需要序列化的字段 ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductSerializerCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'url']

class ShoppingCartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializerCart(source='productID', read_only=True)

    class Meta:
        model = ShoppingCartItem
        fields = ['id', 'cartID', 'productID', 'quantity', 'product_detail']

