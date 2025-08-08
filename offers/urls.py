from django.urls import path

from . import views

urlpatterns = [
    path("", views.offers_view, name="offers"),
    path("view_offer/", views.offer_view)
]
