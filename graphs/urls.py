from logging import log

from django.urls import path

from graphs.views import graphview

# urlpatterns = [
#     url(r'^(?P<symbol>\w+)/$', graphview.as_view() ),
#     url(r'test/(?P<symbol>\w+)/$', testgraphview.as_view() ),
# ]

urlpatterns = [
    path('<str:symbol>', graphview.as_view() ),
    # url(r'test/(?P<symbol>\w+)/$', testgraphview.as_view() ),
]