from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$','gourmetweb.recview.views.index'),
    (r'^sort/(?P<field>.*)/','gourmetweb.recview.views.sort'),
    (r'^search/(?P<term>.*)','gourmetweb.recview.views.search'),
    (r'^rec/do_search/','gourmetweb.recview.views.do_search'),
    (r'^rec/do_search_xhr/','gourmetweb.recview.views.do_search_xhr'),
    (r'^regexp/(?P<term>.*)','gourmetweb.recview.views.regexp'),
    (r'^rec/$','gourmetweb.recview.views.index'),    
    (r'^rec/(?P<rec_id>\d*)/$','gourmetweb.recview.views.rec'),
    (r'^rec/(?P<rec_id>\d*)/(?P<mult>[\d.]*)$','gourmetweb.recview.views.rec'),
    (r'^shop/$','gourmetweb.recview.views.shop'),    
    (r'^shop/(?P<rec_id>\d*)/$','gourmetweb.recview.views.shop'),
    (r'^shop/(?P<rec_id>\d*)/(?P<mult>[\d.]*)$','gourmetweb.recview.views.shop'),
    (r'^shop/remove/(?P<rec_id>\d*)/$','gourmetweb.recview.views.shop_remove'),
    (r'^shop/to_pantry/','gourmetweb.recview.views.shop_to_pantry'),
    (r'^shop/to_list/','gourmetweb.recview.views.shop_to_list'),    
    (r'^rec/multiply/','gourmetweb.recview.views.multiply_rec'),
    (r'^img/(?P<rec_id>\d*)/$','gourmetweb.recview.views.img'),
    (r'^thumb/(?P<rec_id>\d*)/$','gourmetweb.recview.views.thumb'),    
    (r'^rec/multiply_xhr/','gourmetweb.recview.views.multiply_rec_xhr'),
    (r'^js/(?P<path>.*)$','django.views.static.serve',{'document_root':'/home/tom/Projects/grecipe-manager/src/lib/plugins/web_plugin/gourmetweb/templates/'}),
    #(r'^shop/(?P<rec_id>\d*)/(?P<mult>\d)/$','gourmetweb.recview.views.shop'),
    # Example:
    # (r'^gourmet/', include('gourmet.foo.urls')),
                       
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
