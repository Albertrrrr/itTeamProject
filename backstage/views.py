from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import productCategory
from .serializer import ProductCategorySerializer


# Create your views here.
class ProductCategoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):

        if pk:
            try:
                product_category = productCategory.objects.get(pk=pk)
                serializer = ProductCategorySerializer(product_category)
                return Response(serializer.data)
            except productCategory.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            product_categories = productCategory.objects.all()
            serializer = ProductCategorySerializer(product_categories, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            product_category = productCategory.objects.get(pk=pk)
            serializer = ProductCategorySerializer(product_category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except productCategory.DoesNotExist:
            return Response({"error": "Please Check"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            product_category = productCategory.objects.get(pk=pk)
            product_category.delete()
            return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)
        except productCategory.DoesNotExist:
            return Response({"error": "Please Check"}, status=status.HTTP_404_NOT_FOUND)
