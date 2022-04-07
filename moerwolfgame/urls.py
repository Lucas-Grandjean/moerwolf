from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('lobby', views.lobby, name="lobby"),
    path('game/<int:urlgameid>', views.game, name='game'),
    path('chat/<int:urlgameid>', views.chat, name='chat'),
    path('actions<int:urlgamerole>/<int:urlgameid>', views.actions, name='actions'),
]
