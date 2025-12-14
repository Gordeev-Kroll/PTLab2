from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("apply_promo/", views.apply_promo, name="apply_promo"),
    path("buy/<int:product_id>/", views.PurchaseCreate.as_view(), name="buy"),
]
