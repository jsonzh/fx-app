from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rate$', views.rates, name='rates'),
    url(r'^rate/(?P<currency>\w+)/(?P<period>\d+)/$', views.rates_json, name='rates_json'),
]
