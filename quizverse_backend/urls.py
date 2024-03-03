"""
URL configuration for quizverse_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from ninja import NinjaAPI

api = NinjaAPI(title="Quizverse API", version="0.1.0")

api.add_router("/auth/", "users.views.router", tags=["auth"])
api.add_router("/quiz/", "quiz_viva.views.router", tags=["quiz"])
api.add_router("/admin/", "admin.views.router", tags=["admin"])
urlpatterns = [
    path("api/v1/", api.urls),
]
