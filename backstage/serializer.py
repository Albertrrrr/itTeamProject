from rest_framework import serializers
from .models import productCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = productCategory
        fields = '__all__'  # 列出所有需要序列化的字段 ['id', 'name', 'description']
