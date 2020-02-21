from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add),
    path('detail/', views.detail),
    path('feback/', views.feback),
]