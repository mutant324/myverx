from django.contrib import admin  # noqa админ не работает без орм, но строку оставил чтоб не забыть что ее тут не должно быть
from django.urls import path, include

urlpatterns = [
    path('', include('shop.urls')),
]
