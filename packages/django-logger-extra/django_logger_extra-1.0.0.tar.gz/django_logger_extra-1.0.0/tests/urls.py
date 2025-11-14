from django.urls import path

from . import views

urlpatterns = [
    path("nop", views.nop),
    path("hello", views.hello),
    path("parrot", views.parrot),
    path("error", views.error),
]
