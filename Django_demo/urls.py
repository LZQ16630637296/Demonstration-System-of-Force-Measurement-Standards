"""
URL configuration for Django_demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include

#from std_app.views import test
from std_app import urls as std_app_urls
from node_info import urls as node_info_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("test/", include(std_app_urls, namespace='test')),
#    path("test/", test)
    path("", include(node_info_urls, namespace='node_info')),
]
