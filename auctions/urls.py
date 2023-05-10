from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("catagory", views.catagory, name="catagory"),
    path("listing", views.listing, name="listing"),
    path("create-listing", views.create_listing, name="create_listing")
]
