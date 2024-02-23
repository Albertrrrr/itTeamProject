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
from backstage.views import ProductCategoryView, ProductView, ProductDetailView, ShoppingCartView
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

]
