from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

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

    path('health/', TemplateView.as_view(template_name="health.html")),

]
