"""nameplate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from kiosk.views import outlook_login, get_token, home, outlook_logout, select_room, set_room

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'login/', outlook_login, name='outlook_login'),
    path(r'logout/', outlook_logout, name='outlook_logout'),
    path(r'get_token/', get_token, name='get_token'),
    path(r'select_room/', select_room, name='select_room'),
    path(r'set_room', set_room, name='set_room'),
    path(r'', home, name='home')
]
