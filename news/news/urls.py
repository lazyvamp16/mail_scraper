"""
URL configuration for geeks_site project.

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
#from news.views import hello_geeks
from news.showmails import get_headers
#from news.fetchemails import hi
from news.getstocks import symbols_json

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fetchemail/', get_headers),
    #path('hi/',hi),
    path('symbols_json/', symbols_json)
]
