"""
URL configuration for itTeamProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from eShop.views import RegisterView, LoginView, SendVerificationCodeView
from backstage.views import ProductCategoryView, ProductView, ProductDetailView, ShoppingCartView, \
    ShoppingCartItemByProductDetail, ShoppingCartItemListCreate, AddressList, AddressDetail,UserOrderAPIView, UserOrderOneAPIView, AliPayAPIView, \
    ManagerOrderOneAPIView, UserOrderCreateAPIView, ProductSearchAPIView
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

schema_view = get_schema_view(title='API Title')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/generateVCode/', SendVerificationCodeView.as_view(), name='v-code'),
    path('api/categories/', ProductCategoryView.as_view(), name='category-list-create'),
    path('api/categories/<int:pk>/', ProductCategoryView.as_view(), name='category-detail-update-delete'),
    path('api/products/', ProductView.as_view(), name='product-list'),
    path('api/products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('schema/', schema_view),
    path('docs/', include_docs_urls(title='API Documentation')),
    path('api/shopping-cart/<int:user_id>/', ShoppingCartView.as_view(), name='shopping-cart-detail'),
    path('api/shopping-cart-items/cart/<int:cart_id>/', ShoppingCartItemListCreate.as_view(),
         name='shopping-cart-item-list-create'),
    path('api/search/products/', ProductSearchAPIView.as_view(), name='product-search'),
    path('api/shopping-cart-items/item/<int:pk>/', ShoppingCartItemByProductDetail.as_view(),
         name='shopping-cart-item-by-product-detail'),
    path('api/users/<int:user_id>/addresses/', AddressList.as_view(), name='address-list'),
    path('api/users/<int:user_id>/addresses/<int:pk>/', AddressDetail.as_view(), name='address-detail'),
    path('api/users/<int:user_id>/orders/', UserOrderAPIView.as_view(), name='user-orders'),
    path('api/users/create/<int:user_id>/orders/', UserOrderCreateAPIView.as_view(), name='order-create'),
    path('api/users/<int:user_id>/orders/<int:pk>/', UserOrderOneAPIView.as_view(), name='user-order-detail'),
    path('api/alipay/<int:user_id>/<int:pk>/', AliPayAPIView.as_view(), name='alipay'),
    path('api/manager/orders/', ManagerOrderOneAPIView.as_view(), name='manager-user-orders'),
]
