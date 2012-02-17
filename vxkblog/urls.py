from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from . import views
from feeds import LatestEntries

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'blog/entry_index.html'}, 
        name='blog_entry_index'),
    url(r'^(?P<year>\d{4})/$', views.entry_archive_year,
        name='blog_entry_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<slug>[a-z0-9\-]+)/$', views.entry_detail,
        name='blog_entry_detail'),
    url(r'^(?P<year>\d{4})/(?P<slug>[a-z0-9\-]+)/preview/$', views.entry_preview,
        name='blog_entry_preview'),
    url(r'^feed/$', LatestEntries(), name='blog_feeds'),
)
