from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('connexion', views.signin, name="signin"),
    path('deconnexion', views.signout, name="signout"),
    path('inscription', views.signup, name="signup"),
    path('listecartes', views.cardlist, name="cardlist"),
    path('regles', views.rules, name="rules"),
]
