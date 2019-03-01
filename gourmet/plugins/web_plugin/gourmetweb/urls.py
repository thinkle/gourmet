from django.conf.urls import url
import django.views.static
from recview import views as rv_views
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^$', rv_views.index, name='index'),
    url(r'^sort/(?P<field>.*)/', rv_views.sort),
    url(r'^search/(?P<term>.*)', rv_views.search),
    url(r'^rec/do_search/', rv_views.do_search),
    url(r'^rec/do_search_xhr/', rv_views.do_search_xhr),
    # url(r'^regexp/(?P<term>.*)', rv_views.regexp),  # regexp is not implemented in recview.views.regexp
    url(r'^rec/$', rv_views.index),
    url(r'^rec/(?P<rec_id>\d*)/$', rv_views.rec),
    url(r'^rec/(?P<rec_id>\d*)/(?P<mult>[\d.]*)$', rv_views.rec),
    url(r'^shop/$', rv_views.shop),
    url(r'^shop/(?P<rec_id>\d*)/$', rv_views.shop),
    url(r'^shop/(?P<rec_id>\d*)/(?P<mult>[\d.]*)$', rv_views.shop),
    url(r'^shop/remove/(?P<rec_id>\d*)/$', rv_views.shop_remove),
    url(r'^shop/to_pantry/', rv_views.shop_to_pantry),
    url(r'^shop/to_list/', rv_views.shop_to_list),
    url(r'^rec/multiply/', rv_views.multiply_rec),
    url(r'^img/(?P<rec_id>\d*)/$', rv_views.img),
    url(r'^thumb/(?P<rec_id>\d*)/$', rv_views.thumb),
    url(r'^rec/multiply_xhr/', rv_views.multiply_rec_xhr),
    url(r'^js/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.TEMPLATE_PATH}),
    # url(r'^shop/(?P<rec_id>\d*)/(?P<mult>\d)/$', rv_views.shop),
    url(r'^about/$', rv_views.about),
    # Example:
    # (r'^gourmet/', include('gourmet.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
]
