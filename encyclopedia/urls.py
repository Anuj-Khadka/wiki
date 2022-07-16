from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.Entry, name="Entry"),
    path("Search", views.Search, name="Search"),
    path("NewPage", views.NewPage, name="NewPage"),
    path("wiki/<str:title>/edit", views.EditPage, name="EditPage"),
    path("wiki/<str:title>/submit", views.SubmitEdit, name="SubmitEdit"),
    path('wiki/', views.Random, name='Random')
]
