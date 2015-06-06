from django.conf.urls import include, url
from django.contrib import admin

from emo_dump import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', views.hello),

    url(r'^$', views.index),

    url(r'^auth/start/$', views.oauth_start),
    url(r'^auth/end/$', views.oauth_end),
    url(r'^auth/del/$', views.oauth_clear),
]
