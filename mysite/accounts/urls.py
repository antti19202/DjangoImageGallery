# accounts/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.registerPage, name="register"),  # /register ohjaa käyttäjätunnusten luontiin
    path('login/', views.loginPage, name="login"),  # /login ohjaa sisäänkirjautumiseen
    path('logout/', views.logoutUser, name="logout"),

    path('', views.home, name="home"),  # Pelkkä ip ohjaa kotisivulle
    path('user/', views.userPage, name="user-page"),  # Käyttäjän oma sivu
    path('settings/', views.accountSettings, name="settings"),  # Käyttäjä pystyy muokkaamaan tietojansa

    path('upload/', views.uploadImage, name="upload"),  # Kuvan lataus sivu
    path('create_album/', views.createAlbum, name="create-album"),
    path('delete_image/', views.deleteImage, name="delete_image"),
    path('delete_album/', views.deleteAlbum, name="delete_album"),
    path('404/', views.pageNotFound, name="404"),
    path('search/', views.search, name="search"),

    path('image_small/<str:pk>/', views.imageViewSmall, name="image_small"),
    path('image_large/<str:pk>/', views.imageViewLarge, name="image_large"),
    path('image/<str:pk>/', views.imageView, name="image"),
    path('album/<str:pk>/', views.albumView, name="album"),

    path('delete_user/<str:username>/', views.deleteUser, name="delete_user"),
    path('delete/<str:pk>/', views.delete, name="delete"),
    path('delete_album_confirm/<str:pk>/', views.deleteAlbumConfirm, name="delete_album_confirm"),

    path('post/<slug:slug>/', views.detail_view, name="detail"),
    path('tag/<slug:slug>/', views.tagged, name="tagged"),
    path('<str:username>/', views.profile, name='profile'),

]