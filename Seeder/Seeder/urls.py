from django.conf.urls import patterns, include, url
from django.contrib import admin
from core import urls as core_urls

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),


    # beware: wild card regexp!
    url(r'^', include(core_urls))
)
