from django.conf.urls import include, url
from django.contrib import admin
from emo_dump import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', views.hello),
    url(r'^tweet/$', views.tweet_test)
]
