from MySQLdb import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from .models import productCategory, Product, ShoppingCart, ShoppingCartItem, Address, Order
from .serializers import ProductCategorySerializer, ProductSerializer, ShoppingCartItemSerializer, AddressSerializer, \
    OrderSerializer, SimpleUserOrderSerializer, SimpleManagerOrderSerializer


# Create your views here.
class ProductCategoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        ### Get All categories
        * Method：Get
        ### Success Response:
            Code: 200 OK
            Content: List of categories
        """
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
        """
        ### Add a new category
        * Method: POST
        * Auth required: Yes
        * Permissions required: Admin
        ### Request Body
             - "name": "[name of the category]",
             - "description": "[description of the category]"

        ### Success Response:
            Code: 201 CREATED
            Content: { "id": 12, "name": "Category Name", "description": "Category Description" }

        """
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        ### Update a specific category
        * Method: PUT
        * Auth required: Yes
        * Permissions required: Admin
        * URL Parameters: id=[integer]
        ### Request Body
          - "name": "[new name of the category]",
          - "description": "[new description of the category]"

        ### Success Response:
            Code: 200 OK
            Content: { "id": 12, "name": "New Category Name", "description": "New Category Description" }

        """
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
        """
        ### Delete a specific category
        * Method: DELETE
        * Auth required: Yes
        * Permissions required: Admin
        * URL Parameters: id=[integer]
        ### Success Response:
            - Code: 204 Delete Successfully
            - Content: None
        """
        try:
            product_category = productCategory.objects.get(pk=pk)
            product_category.delete()
            return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)
        except productCategory.DoesNotExist:
            return Response({"error": "Please Check"}, status=status.HTTP_404_NOT_FOUND)


class ProductView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        ### Retrieve a list of products. Pagination is applied to this endpoint with a default page size of 10.
               Parameters:
               page: A number of the page you want to retrieve (query parameter).
               Responses:
                - 200 OK: Returns a list of products with pagination details.
                - 401 Unauthorized: If the user is not authenticated.
        """
        products = Product.objects.all()
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """
        * Create a new product.
        * Method: POST
        * Auth required: Yes (Token Authentication)
        * Permissions required: IsAuthenticated

        ### Request Body:
             name: [name of the product]
             categoryID: [id of the related category]
             price: [price of the product]
             stock: [stock quantity of the product]
             description: [description of the product]
             URL: [URL of the product image or website]

        ### Success Response:
        - Code: 201 CREATED
        - Content: {
          "id": 12,
          "name": "Product Name",
          "categoryID": 3,
          "price": 19.99,
          "stock": 100,
          "description": "Product Description",
          "URL": "http://example.com/product"
        }

        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        """
        ### Retrieve a specific product.
        * Method: GET
        * Auth required: Yes (Token Authentication)
        * Permissions required: IsAuthenticated

        ### URL Parameters:
            - id: The unique id of the product to retrieve.

        ### Success Response:
            Code: 200 OK
            Content: { "id": 12, "name": "Product Name", "categoryID": 3, "price": 19.99, "stock": 100, "description": "Product Description", "URL": "http://example.com/product" }

        """
        product = self.get_object(id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """
        ### Update a specific product.
        * Method: PUT
        * Auth required: Yes (Token Authentication)
        * Permissions required: IsAuthenticated

        ### URL Parameters:
            - id: The unique id of the product to update.

        ### Request Body:
            - name: [new name of the product]
            - categoryID: [new id of the related category]
            - price: [new price of the product]
            - stock: [new stock quantity of the product]
            - description: [new description of the product]
            - URL: [new URL of the product image or website]

        ### Success Response:
            Code: 200 OK
            Content: { "id": 12, "name": "Updated Product Name", "categoryID": 3, "price": 25.99, "stock": 150, "description": "Updated Product Description", "URL": "http://example.com/updated_product" }
        """
        product = self.get_object(id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        ### Delete a specific product.
        * Method: DELETE
        * Auth required: Yes (Token Authentication)
        * Permissions required: IsAuthenticated

        ### URL Parameters:
            - id: The unique id of the product to delete.

        ### Success Response:
            Code: 204 Message: Delete Successfully
        """
        product = self.get_object(id)
        product.delete()
        return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    ### Retrieve a ShoppingCart ID by CustomUser ID.
    * Request Type: GET
    ### Parameters:
        user_id (URL path parameter): The unique identifier of the user (must be an integer).
    ### Success Response:
        Code: 200 OK
    ### Content Example:
        {
          "shoppingCartID": 12
        }
   ###  Error Response:
        Code: 404 Not Found
        Content: If there is no shopping cart corresponding to the specified user ID, a 404 status code will be returned.
    """

    def get(self, request, user_id, format=None):
        try:
            shopping_cart = ShoppingCart.objects.get(userID=user_id)
            # 直接返回购物车ID
            return JsonResponse({'shoppingCartID': shopping_cart.id})
        except ShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ShoppingCartItemListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # 缺API文档
    def get(self, request, cart_id, format=None):
        items = ShoppingCartItem.objects.filter(cartID__id=cart_id)
        if not items.exists():
            return Response({"error": "Shopping cart not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShoppingCartItemSerializer(items, many=True)

        total_final_price = 0  # 初始化最终价格的总和
        items_with_final_price = []
        for item in serializer.data:
            final_price = item['quantity'] * item['product_detail']['price']
            item_with_final_price = item  # 复制原有数据
            item_with_final_price['final_price'] = final_price
            items_with_final_price.append(item_with_final_price)
            total_final_price += final_price  # 累加最终价格到总和中

        # 构建响应数据，包括所有项的详细信息和最终价格的总和
        response_data = {
            'items': items_with_final_price,
            'total_final_price': total_final_price
        }

        return Response(response_data)

    def post(self, request, cart_id, format=None):
        """
        ### Add an Item to a Specific Shopping Cart
        * Method: POST
        ### URL Parameters:
            cart_id: The ID of the specified shopping cart.
        ### Data Parameters (Request Body):
            productID: The ID of the product to be added to the cart.
            quantity: The quantity of the product to be added.
        ### Success Response:
            Code: 201 Created
            Content: Details of the newly added shopping cart item, including id, cartID, productID, and quantity.
        ### Error Response:
            Code: 400 Bad Request (If the provided data is invalid, such as exceeding available stock)
            Code: 404 Not Found (If the specified shopping cart or product does not exist)
        """
        serializer = ShoppingCartItemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                cart = ShoppingCart.objects.get(id=cart_id)
                product_id = request.data.get('productID')
                product = Product.objects.get(id=product_id)
                # 检查库存是否足够
                requested_quantity = serializer.validated_data.get('quantity')
                if requested_quantity > product.stock:
                    return Response({'quantity': f'Requested quantity exceeds available stock of {product.stock}.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer.save(cartID=cart, productID=product)
                return Response({"message": "Add to shopping cart successfully!"}, status=status.HTTP_201_CREATED)
            except (Product.DoesNotExist, ShoppingCart.DoesNotExist):
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartItemByProductDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        """
        ### Retrieve a Specific Shopping Cart Item
        Method: GET
        URL Parameters:
        pk: The primary key ID of the shopping cart item. This ID is used internally and is not directly visible to the user.
        Success Response:
        Code: 200 OK
        Content: Returns only the quantity of the specific shopping cart item, e.g., {"quantity": 3}.
        Error Response:
        Code: 404 Not Found (If the specified shopping cart item does not exist).
        """
        cart_item = get_object_or_404(ShoppingCartItem, pk=pk)
        # Return only the quantity of the shopping cart item
        return Response({'quantity': cart_item.quantity})

    def put(self, request, pk, format=None):
        """
        ### Update the Quantity of a Specific Shopping Cart Item
        * Method: PUT
        ### URL Parameters:
            pk: The primary key ID of the shopping cart item. This ID is intended for internal use and should not be exposed to the user.
        ### Data Parameters (Request Body):
            quantity: The new quantity for the shopping cart item. This is the only attribute that users are allowed to modify.
        ### Success Response:
            Code: 200 OK Update successfully
        ### Error Response:
            Code: 400 Bad Request (If the quantity is not provided in the request body).
            Code: 404 Not Found (If the specified shopping cart item does not exist).
        """
        cart_item = get_object_or_404(ShoppingCartItem, pk=pk)
        # Only allow updating the quantity
        quantity = request.data.get('quantity')
        if quantity is not None:
            cart_item.quantity = quantity
            cart_item.save()
            return Response({'message': "Update successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Quantity is required.'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        ### Delete a Specific Shopping Cart Item
        * Method: DELETE
        ### URL Parameters:
            pk: The primary key ID of the shopping cart item. This parameter is used for internal tracking and is not visible to the user.
        ### Success Response:
            Code: 204 {"message": "Delete Successfully"}
        ### Error Response:
            Code: 404 Not Found (If the specified shopping cart item does not exist).

        """
        cart_item = get_object_or_404(ShoppingCartItem, pk=pk)
        cart_item.delete()
        return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)


class AddressList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    List all addresses for a given user, or create a new address.
    """

    def get(self, request, user_id):
        addresses = Address.objects.filter(user_id=user_id)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update, or delete an address instance.
    """

    def get_object(self, user_id, pk):
        try:
            return Address.objects.get(pk=pk, user_id=user_id)
        except Address.DoesNotExist:
            raise Http404

    def get(self, request, user_id, pk):
        address = self.get_object(user_id, pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, user_id, pk):
        address = self.get_object(user_id, pk)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, pk):
        address = self.get_object(user_id, pk)
        address.delete()
        return Response({'message': "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)


class UserOrderOneAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id, pk):
        try:
            return Order.objects.get(id=pk, user_id=user_id)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, user_id, pk):
        order = self.get_object(user_id, pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, user_id, pk):
        order = self.get_object(user_id, pk)
        order.status = 'cancel'
        try:
            order.save()
            serializer = OrderSerializer(order)
            return Response({'message': "Update successfully!", 'order': serializer.data}, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, user_id, pk):
        order = self.get_object(user_id, pk)
        if order.status == 'delivered':
            order.status = 'done'
            try:
                order.save()
                serializer = OrderSerializer(order)
                return Response({'message': "Your order have been done! Thanks! ", 'order': serializer.data},
                                status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)


class UserOrderAPIView(APIView):
    """
    List all orders for a given user, or create a new order for the user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        orders = Order.objects.filter(user_id=user_id).order_by('id')
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = SimpleUserOrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request, user_id):
        try:
            # 假设每个用户只有一个购物车
            cart = ShoppingCart.objects.get(userID_id=user_id)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Shopping cart not found."}, status=status.HTTP_404_NOT_FOUND)

        address_id = request.data.get('address_id')
        try:
            # 根据地址ID获取地址实例
            address = Address.objects.get(pk=address_id, user_id=user_id)
        except Address.DoesNotExist:
            return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

            # 序列化地址信息
        address_serializer = AddressSerializer(address)

        items = ShoppingCartItem.objects.filter(cartID_id=cart)
        if not items.exists():
            return Response({"error": "Shopping cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ShoppingCartItemSerializer(items, many=True)

        total_final_price = 0  # 初始化最终价格的总和
        items_with_final_price = []
        for item in serializer.data:
            final_price = item['quantity'] * item['product_detail']['price']
            item_with_final_price = item  # 复制原有数据
            item_with_final_price['final_price'] = final_price
            items_with_final_price.append(item_with_final_price)
            total_final_price += final_price  # 累加最终价格到总和中

        order_data = {
            'user': user_id,
            'item': items_with_final_price,  # 确保这里符合OrderSerializer的期望格式
            'totalCost': total_final_price,
            'address': address_serializer.data
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()
            # 清空购物车中的记录
            items.delete()
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
