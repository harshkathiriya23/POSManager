from django.urls import path

from products import views

urlpatterns = [
    path("list/", views.ProductListView.as_view(), name="product_list"),
    path("stock/", views.ProductStockView.as_view(), name="product_stock"),
    path("category/add/", views.CategoryCreateView.as_view(), name="category_add"),
    path("product/add/", views.ProductCreateView.as_view(), name="product_add"),
    path("product/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("product/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
]
