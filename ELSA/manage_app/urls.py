from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add),
    path('detail/', views.detail),
    path('feedback/', views.feedback),
    path('use/', views.use),
    path('plan/', views.plan),
    path('technology/', views.technology),
    path('theory/', views.theory),
    path('reference/', views.reference),
    path('resume/', views.resume),
]