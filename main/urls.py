from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('unit/', views.UnitView.as_view(), name="unit"),
    path('closure/', views.OrgChartView.as_view(), name="closure")
]
