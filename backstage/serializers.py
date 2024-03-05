from rest_framework import serializers
from .models import productCategory, Product, ShoppingCartItem, Address, Order


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = productCategory
        fields = '__all__'  # 列出所有需要序列化的字段 ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()  # 添加一个自定义字段

    class Meta:
        model = Product
        fields = '__all__'  # 或者你也可以明确列出所有字段加上'category_name'

    def get_category_name(self, obj):
        # 检查categoryID是否存在，避免在未设置时引发异常
        if obj.categoryID:
            return obj.categoryID.name
        return None  # 如果没有关联的categoryID，返回None


class ProductSerializerCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'url']

class ShoppingCartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializerCart(source='productID', read_only=True)

    class Meta:
        model = ShoppingCartItem
        fields = ['id', 'cartID', 'productID', 'quantity', 'product_detail']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'house_number_and_street', 'area', 'town', 'county', 'postcode', 'country']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'item', 'address', 'totalCost', 'createTime', 'finishTime', 'status', 'isPaid']
        read_only_fields = ['id', 'createTime']

class SimpleUserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'createTime', 'totalCost', 'status', 'isPaid']

class SimpleManagerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'createTime', 'totalCost', 'status', 'isPaid']