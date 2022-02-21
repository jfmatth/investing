from django.contrib import admin
from django.urls import path, include

from aim.views import IndexView 


urlpatterns = [
    #admin of course
    path('admin/', admin.site.urls),
       
    # django-allauth
    path('accounts/', include('allauth.urls')),

    # Root
    path('', IndexView.as_view(), name="index" ),

    # application aim
    path('aim/', include('aim.urls')),

    path('graph/', include('graphs.urls')),

]
