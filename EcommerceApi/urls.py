"""
URL configuration for EcommerceApi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework import routers
from django.conf.urls.static import static
from product_app.views import ProductViewSet, CategoryViewSet, BrandViewSet
from . import settings

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"brands", BrandViewSet, basename="brands")

urlpatterns = [
                  path("", include(router.urls)),
                  path('admin/', admin.site.urls),
                  path('user/', include("user_auth_app.urls")),
                  path('product/', include("product_app.urls")),
                  path('cart/', include("cart_app.urls")),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
