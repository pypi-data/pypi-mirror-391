from django.urls import path
from .views import select2plus_api

urlpatterns = [
    path("api/", select2plus_api, name="select2plus_api"),
    
]
