import datetime
import os
from MySQLdb import IntegrityError
from alipay import AliPay, AliPayConfig
from django.db.models import Q
from django.http import Http404, JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from .models import productCategory, Product, ShoppingCart, ShoppingCartItem, Address, Order
from .serializers import ProductCategorySerializer, ProductSerializer, ShoppingCartItemSerializer, AddressSerializer, \
    OrderSerializer, SimpleUserOrderSerializer, SimpleManagerOrderSerializer
from backstage.tasks import query_order_status


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
        ### Instance:
            Token
            127.0.0.1:8000/api/categories/
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
        ### Instance:
            {
                "name":"Faimly Kit",
                "description": "Kit"
            }

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

        ### Instance:
            {
                "name": "Vegetarian",
                "description": "Update Kit"
            }

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
        ### Instance:
            127.0.0.1:8000/api/categories/6/
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
        ### Instance:
            127.0.0.1:8000/api/products/
        ###  Responses:
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

        ### Instance:
            {
                "name":"TestProducts2",
                "categoryID":"4",
                "price":"1.83",
                "stock":"100",
                "description":"key",
                "URL":"https://.git"
            }

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

        ### Instance:
            127.0.0.1:8000/api/products/1/

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
        ### Instance:
            127.0.0.1:8000/api/products/1/
             {
                 "name":"TestName",
                "categoryID":"3",
                "price":"2.38",
                "stock":"100",
                "description":"key",
                "url":"https://mm.com.fig"
             }
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

        ### Instance:
            127.0.0.1:8000/api/products/1/

        ### Success Response:
            Code: 204 Message: Delete Successfully
        """
        product = self.get_object(id)
        product.delete()
        return Response({"message": "Delete Successfully"}, status=status.HTTP_204_NO_CONTENT)


class ProductSearchAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    User Search
    """
    def post(self, request, *args, **kwargs):
        """
            ### URL:
                POST /api/search/products/
            ### Description :This endpoint allows authenticated users to search for products by name, ignoring case sensitivity. It returns a paginated list of products that contain the specified query in their name.

            ### Authentication
                Required. Token-based authentication is used to secure access to this endpoint. Users must provide a valid authentication token in the header of their request.
                Permissions
                Required. Users must be authenticated to access this endpoint.
            ### Request Parameters
            ### Body Parameters:
                name (string): The name or partial name of the product to search for. This parameter is case-insensitive.
            ### Responses
                200 OK: The request was successful, and the response contains a paginated list of products matching the search criteria.
                The response includes fields such as id, name, categoryID, price, stock, description, and url for each product, depending on the fields defined in the ProductSerializer.
                400 Bad Request: The request failed due to missing or invalid parameters. A message explaining the reason for the failure is included in the response body.
                Example: {"message": "Name parameter is missing."}

            ### Instance:
                Content-Type: application/json
                Authorization: Token YOUR_AUTH_TOKEN_HERE
                127.0.0.1:8000/api/search/products/
                {
                    "name":"2"
                }
            """
        name_query = request.data.get('name', None)
        if name_query is not None:
            # Case-insensitive searches using icontains
            products = Product.objects.filter(name__icontains=name_query)
            paginator = pagination.PageNumberPagination()
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({"message": "Name parameter is missing."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        ### Description:
            This endpoint retrieves a paginated list of products filtered by a specific category. It requires clients to provide a category ID as a query parameter to filter products accordingly. If the category ID is not provided, the API responds with an error message indicating that the category parameter is missing.
        ### Request Parameters:
            Query Parameters:
            category (integer, required): The unique identifier (ID) of the category to filter products by.
        ### Instance:
            URL: 127.0.0.1:8000/api/search/products/?category=2
        ### Responses:
            200 OK: Successfully retrieved a list of products for the specified category. The response is paginated and includes details of each product, such as product ID, name, category ID, price, stock, description, and URL.
            400 Bad Request: The request failed due to missing the required category parameter. An error message is included in the response body.
        """
        category = request.query_params.get("category", None)
        if category is not None:
            products = Product.objects.filter(categoryID=category).order_by("id")
            paginator = pagination.PageNumberPagination()
            result_page = paginator.paginate_queryset(products, request)
            serializer = ProductSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({"message": "category parameter is missing."}, status=status.HTTP_400_BAD_REQUEST)

class ShoppingCartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """
        ### Retrieve a ShoppingCart ID by CustomUser ID.
        ### Request Type: GET
        ### Parameters:
            user_id (URL path parameter): The unique identifier of the user (must be an integer).
        ### Instance:
            127.0.0.1:8000/api/shopping-cart/10/
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
        """
        ### Description:
            This endpoint retrieves all items within a specified shopping cart, including the final price for each item based on its quantity and the individual product price. It also calculates and returns the total final price of all items in the cart. The endpoint is designed to provide detailed information about the shopping cart contents for review or checkout purposes.
        ### Parameters:
            Path Parameters:
            cart_id (integer): The unique identifier of the shopping cart whose items are to be retrieved.
        ### Instance:
            127.0.0.1:8000/api/shopping-cart-items/cart/1/
        ### Responses
            200 OK: Successfully retrieved the shopping cart items along with their final prices.
            The response body includes an array of items, each with product details and a calculated final_price, as well as the total_final_price for the entire cart.
            404 Not Found: The specified shopping cart does not exist or contains no items. An error message is included in the response body.
        ### Example:
            {"error": "Shopping cart not found."}


        """
        items = ShoppingCartItem.objects.filter(cartID__id=cart_id)
        if not items.exists():
            return Response({"error": "Shopping cart not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShoppingCartItemSerializer(items, many=True)

        total_final_price = 0  # Initialise the sum of the final prices
        items_with_final_price = []
        for item in serializer.data:
            final_price = item['quantity'] * item['product_detail']['price']
            item_with_final_price = item  # Copy to
            item_with_final_price['final_price'] = final_price
            items_with_final_price.append(item_with_final_price)
            total_final_price += final_price  # Accumulate the final price into the sum

        total_final_price = round(total_final_price, 2)
        # Constructing the response data, including details of all items and the sum of the final prices
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
        ### Instance:
            127.0.0.1:8000/api/shopping-cart-items/cart/1/
            {
                "cartID":"1",
                "productID":"4",
                "quantity":"30"
            }
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
                # Checking the adequacy of stock
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
        ### Instance:
            127.0.0.1:8000/api/shopping-cart-items/item/30/
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
        ### Instance:
            127.0.0.1:8000/api/shopping-cart-items/item/30/
            {"quantity":60}
        ### Success Response:
            Code: 200 OK Update successfully
        ### Error Response:
            Code: 400 Bad Request (If the quantity is not provided in the request body). or "The quantity exceeds the available stock."
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
        ### Instance:
            127.0.0.1:8000/api/shopping-cart-items/item/30/
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
        """
        ### Description:
            Retrieves a list of all addresses associated with the specified user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user whose addresses are to be retrieved.
        ### Instance:
            127.0.0.1:8000/api/users/10/addresses/
        ### Responses:
            200 OK: Successfully retrieved a list of addresses. The response body includes an array of address records for the specified user.
            404 Not Found: The specified user does not exist or has no addresses. An appropriate error message is included in the response body.

        """
        addresses = Address.objects.filter(user_id=user_id)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        """
        ### Description:
            Creates a new address for the specified user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user for whom the address is being created.
        ### Body Parameters:
            Required. The address details to be created (user, house_number_and_street, area, town, county, postcode).
        ### Instance:
            URL: 127.0.0.1:8000/api/users/10/addresses/
            {
                "user":"10",
                "house_number_and_street":"Flat 28, 1 Beith Street ",
                "area" : "",
                "town" : "Glasgow",
                "county": "",
                "postcode":"G115PS"

            }
        ### Responses
            201 Created: The address was successfully created. The response body includes the details of the newly created address.
            400 Bad Request: The request failed due to invalid input. An error message detailing the validation errors is included in the response body.
        """
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
        """
        ### Description:
            Retrieves the details of a specific address for the specified user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the address to retrieve.
        ### Instance:
            127.0.0.1:8000/api/users/10/addresses/1
        ### Responses:
            200 OK: Successfully retrieved the address. The response body includes the details of the requested address.
            404 Not Found: The specified address does not exist. An appropriate error message is included in the response body.
        """
        address = self.get_object(user_id, pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, user_id, pk):
        """
        ### Description:
            Updates the specified address for the given user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the address to update.
        ### Body Parameters:
            Required. The updated address details  (user, house_number_and_street, area, town, county, postcode).
        ### Instance:
            127.0.0.1:8000/api/users/10/addresses/1/
            {
                "user":"10",
                "house_number_and_street":"Flat 28, 1 Beith Street ",
                "area" : "",
                "town" : "Glasgow",
                "county": "",
                "postcode":"G115PS"
            }
        ### Responses:
            200 OK: The address was successfully updated. The response body includes the details of the updated address.
            400 Bad Request: The request failed due to invalid input. An error message detailing the validation errors is included in the response body.
        """
        address = self.get_object(user_id, pk)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, pk):
        """
        ### Description:
            Deletes the specified address for the given user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the address to delete.
        ### Instance:
            127.0.0.1:8000/api/users/10/addresses/1/
        ### Responses:
            204 No Content: The address was successfully deleted. A message confirming the deletion is included in the response body.
            404 Not Found: The specified address does not exist. An appropriate error message is included in the response body.
        """
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
        """
        ### Description:
            Retrieves the details of a specific order for the specified user.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the order to retrieve.
        ### Instance:
            127.0.0.1:8000/api/users/10/orders/1/
        ### Responses:
            200 OK: Successfully retrieved the order. The response body includes the details of the requested order.
            404 Not Found: The specified order does not exist. An appropriate error message is included in the response body.
        """
        order = self.get_object(user_id, pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, user_id, pk):
        """
        ### Description:
            Updates the status of the specified order to 'cancel'.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the order to update.
        ### Instance:
            127.0.0.1:8000/api/users/10/orders/1/
        ### Responses:
            200 OK: The order was successfully updated to 'cancel'. The response body includes a success message and the updated order details.
            400 Bad Request: The request failed. An error message is included in the response body.
        """
        order = self.get_object(user_id, pk)
        order.status = 'cancel'
        try:
            order.save()
            serializer = OrderSerializer(order)
            return Response({'message': "Update successfully!", 'order': serializer.data}, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, user_id, pk):
        """
        ### Description:
            Marks the specified order as completed if its status is 'delivered'. It also updates the order's finish time to the current date and time.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user.
            pk (integer): The primary key of the order to mark as completed.
        ### Instance:
            URL: 127.0.0.1:8000/api/users/10/orders/14/
        ### Responses:
            200 OK: The order was successfully marked as completed. The response body includes a success message, and the updated order details.
            400 Bad Request: The request failed due to the order not being in a 'delivered' status or other issues. An error message is included in the response body.
        """
        order = self.get_object(user_id, pk)
        if order.status == 'delivered':
            order.status = 'done'
            now = datetime.datetime.now()
            order.finishTime = now
            try:
                order.save()
                serializer = OrderSerializer(order)
                return Response({'message': "Your order have been done! Thanks! ", 'order': serializer.data},
                                status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)


class ManagerOrderOneAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        ### Description:
            Retrieves a paginated list of all orders sorted by their ID.
        ### Instance:
            URL:127.0.0.1:8000/api/manager/orders/
        ### Responses:
            200 OK: Successfully retrieved a list of orders. The response is paginated and includes order details based on the SimpleManagerOrderSerializer.
        """
        orders = Order.objects.all().order_by('id')
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = SimpleManagerOrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def put(self, request):
        """
        ### Description:
            Updates the status of a specified order to 'delivered', provided the order has been paid.
        ### Request Body:
            id (integer): The unique identifier of the order to update.
        ### Instance:
            URL:127.0.0.1:8000/api/manager/orders/
            {"id":"14"}
        ### Responses:
            200 OK: Successfully updated the order status to 'delivered'. The response includes a success message and the updated order details.
            400 Bad Request: The request failed due to the order not being paid or other issues. An error message is included in the response body.
        """
        pk = request.data.get('id')
        order = Order.objects.get(id=pk)
        if order.isPaid:
            order.status = 'delivered'
            try:
                order.save()
                serializer = OrderSerializer(order)
                return Response({'message': "Update successfully!", 'order': serializer.data},
                                status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({'message': "Unsuccessfully!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Customer need to finish the payment !"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
        ### Description:
            Allows for filtering orders based on user ID, a list of statuses, and a creation date range. It returns a paginated list of orders that match the specified criteria.
        ### Request Body:
            user_id (integer, optional): The unique identifier of the user whose orders to filter.
            statuses (list of strings, optional): A list of order statuses to filter by.
            start_date (string, optional): The start date for filtering orders by creation date, in YYYY-MM-DD format.
            end_date (string, optional): The end date for filtering orders by creation date, in YYYY-MM-DD format.
        ### Instance:
            URL: 127.0.0.1:8000/api/manager/orders/
            {
               "user_id": null,
              "statuses": ["unpaid", "processing"],
              "start_date": "2024-01-01",
              "end_date": "2024-02-28"
            }
        ### Responses:
            200 OK: Successfully retrieved a filtered list of orders. The response is paginated and includes order details based on the criteria specified in the request body.
            400 Bad Request: The request failed due to invalid input or other issues. An error message is included in the response body.
        """
        from datetime import datetime

        user_id = request.data.get('user_id', None)
        statuses = request.data.get('statuses', [])  # Now accepting the status list
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)

        queries = Q()

        # User ID Query Criteria
        if user_id is not None:
            queries &= Q(user_id=user_id)

        # Multiple status query conditions
        if statuses:
            queries &= Q(status__in=statuses)  # Use __in to filter multiple states

        # Create a time range query condition
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            queries &= Q(createTime__range=(start_datetime, end_datetime))

        # executing query
        orders = Order.objects.filter(queries).order_by('id')

        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = SimpleManagerOrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserOrderAPIView(APIView):
    """
    List all orders for a given user, or create a new order for the user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        ### Description:
            Retrieves a paginated list of all orders for the specified user, sorted by order ID.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user whose orders are to be listed.
        ### Instance:
            127.0.0.1:8000/api/users/10/orders/
        ### Responses:
            200 OK: Successfully retrieved a list of orders for the user. The response is paginated and includes details of each order.
            404 Not Found: The specified user does not exist or has no orders. An appropriate error message is included in the response body.
        """
        orders = Order.objects.filter(user_id=user_id).order_by('id')
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = SimpleUserOrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, user_id, *args, **kwargs):
        """
        ### Description:
            Allows filtering of orders for the specified user based on a list of statuses and a creation date range. This method facilitates advanced searching and filtering of user orders.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user whose orders are to be filtered.
            Body Parameters:
            statuses (list of strings, optional): A list of order statuses to filter by.
            start_date (string, optional): The start date for filtering orders by creation date, in YYYY-MM-DD format.
            end_date (string, optional): The end date for filtering orders by creation date, in YYYY-MM-DD format.
        ### Instance:
            URL:127.0.0.1:8000/api/users/10/orders/
            {
              "statuses": ["unpaid","processing","Done"],
              "start_date": "2024-01-01",
              "end_date": "2024-02-28"
            }
        ### Responses:
            200 OK: Successfully retrieved a filtered list of orders for the user. The response is paginated and includes details of each order that matches the filter criteria.
            400 Bad Request: The request failed due to invalid input, such as an incorrect date format. An error message detailing the reason for failure is included in the response body.
        """
        from datetime import datetime
        statuses = request.data.get('statuses', [])  # Now accepting the status list
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date', None)

        # Basic query: User ID
        if user_id is not None:
            queries = Q(user_id=user_id)

            # Status query condition (if provided)
            if statuses:
                queries &= Q(status__in=statuses)

            # Create a time range query condition (if start and end dates are provided)
            if start_date and end_date:
                try:
                    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                    queries &= Q(createTime__range=(start_datetime, end_datetime))
                except ValueError:
                    return Response({"error": "Invalid date format. Please use YYYY-MM-DD."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # perform a search
            orders = Order.objects.filter(queries).order_by('id')

            paginator = pagination.PageNumberPagination()
            result_page = paginator.paginate_queryset(orders, request)
            serializer = SimpleUserOrderSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)


class UserOrderCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        """
         ### Description:
            This endpoint allows for the creation of a new order for a given user based on the contents of their shopping cart and a specified delivery address. It validates the existence of the shopping cart and address, calculates the total price of the cart items, and persists the order. Upon successful creation, the shopping cart items are cleared.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user for whom the order is being created.
        ### Body Parameters:
            address_id (integer): The unique identifier of the delivery address for the new order.
        ### Instance:
            URL: 127.0.0.1:8000/api/users/create/10/orders/
            {"address_id":"3"}
        ### Responses:
            201 Created: The order was successfully created. The response includes the details of the newly created order.
            404 Not Found: Either the shopping cart or the specified address does not exist. An appropriate error message is included in the response body.
            400 Bad Request: The shopping cart is empty, or there was an error in the order data validation. An error message detailing the reason for the failure is included in the response body.

        """
        try:

            cart = ShoppingCart.objects.get(userID_id=user_id)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Shopping cart not found."}, status=status.HTTP_404_NOT_FOUND)

        address_id = request.data.get('address_id')
        try:
            # Example of getting an address based on an address ID
            address = Address.objects.get(pk=address_id, user_id=user_id)
        except Address.DoesNotExist:
            return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

            # Serialising address information
        address_serializer = AddressSerializer(address)

        items = ShoppingCartItem.objects.filter(cartID_id=cart)
        if not items.exists():
            return Response({"error": "Shopping cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ShoppingCartItemSerializer(items, many=True)

        total_final_price = 0  # Initialise the sum of the final prices
        items_with_final_price = []
        for item in serializer.data:
            final_price = item['quantity'] * item['product_detail']['price']
            item_with_final_price = item
            item_with_final_price['final_price'] = final_price
            items_with_final_price.append(item_with_final_price)
            total_final_price += final_price

        order_data = {
            'user': user_id,
            'item': items_with_final_price,
            'totalCost': total_final_price,
            'address': address_serializer.data
        }

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order_serializer.save()
            # Empty Shopping Cart
            items.delete()
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AliPayAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, pk):
        """
        ### Request:
            GET Method: The request does not require anybody payload; instead, it uses user_id and pk (order ID) path parameters to identify the specific order.
        ### Parameters:
            Path Parameters:
            user_id (integer): The unique identifier of the user making the payment.
            pk (integer): The primary key of the order for which the payment is being processed.
        ### Instance:
            URL: 127.0.0.1:8000/api/alipay/10/14/
        ### Responses:
            200 OK: Successfully generated the AliPay payment URL. The response includes the pay_url which can be used to redirect the user to complete the payment.
            404 Not Found: The specified order does not exist. An appropriate error message is included in the response body.
        """

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

        # Output path, for validation only
        print("App Private Key Path:", app_private_key_path)
        print("Alipay Public Key Path:", alipay_public_key_path)


        alipay = AliPay(
            appid="9021000129661967",
            app_notify_url=None,  # Do not receive asynchronous notifications
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True,
            config=AliPayConfig(timeout=15)
        )

        order = Order.objects.get(id=pk, user_id=user_id)

        rounded_number = round(order.totalCost, 2)
        # Generate payment url
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order.id,
            total_amount=str(rounded_number),  # Convert Decimal to String Pass
            subject="P",
            return_url=None,  # Doesn't care about the page jump after the user completes payment
            notify_url=None
        )

        # Sandboxed environments with sandboxed gateways
        pay_url = f"https://openapi-sandbox.dl.alipaydev.com/gateway.do?{order_string}"

        query_order_status.delay(order.id)
        # print(add.delay(10,5))

        # Returns the payment link directly to the front-end without a page jump
        return Response({"pay_url": pay_url})
