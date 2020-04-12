from django.conf.urls import *
from . import views

app_name = "harvester"

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^sources/$', views.sources, name='sources'),
    url('^sources/add/$', views.add_source, name='add_source'),
    url('^sources/(?P<id>\d+)/$', views.source, name='source'),
    url('^sources/(?P<id>\d+)/change/$', views.change_source, name='change_source'),
    url('^sources/(?P<id>\d+)/delete/$', views.delete_source, name='delete_source'),
    url('^sources/(?P<source_id>\d+)/collect_source/$', views.collect_source, name='collect_source'),
    url('^sources/(?P<source_id>\d+)/files/add/$', views.add_source_file, name='add_source_file'),
    url('^sources/(?P<source_id>\d+)/files/(?P<id>\d+)/$', views.source_file, name='source_file'),
    url('^sources/(?P<source_id>\d+)/files/(?P<id>\d+)/change/$', views.change_source_file, name='change_source_file'),
    url('^sources/(?P<source_id>\d+)/files/(?P<id>\d+)/delete/$', views.delete_source_file, name='delete_source_file'),
    url(
        '^sources/(?P<source_id>\d+)/harvesting_rules/add/$',
        views.add_harvesting_rule,
        name='add_harvesting_rule'
    ),
    url(
        '^sources/(?P<source_id>\d+)/harvesting_rules/(?P<id>\d+)/change/$',
        views.change_harvesting_rule,
        name='change_harvesting_rule'
    ),
    url(
        '^sources/(?P<source_id>\d+)/harvesting_rules/(?P<id>\d+)/delete/$',
        views.delete_harvesting_rule,
        name='delete_harvesting_rule'
    ),

    url(
        '^sources/(?P<source_id>\d+)/harvesting_rules/(?P<id>\d+)/collect/$',
        views.run_harvesting_rule,
        name='run_harvesting_rule'
    ),

    url(
        '^sources/(?P<source_id>\d+)/harvesting_journal/$',
        views.harvesting_journal,
        name='harvesting_journal'
    ),
    url(
        '^sources/(?P<source_id>\d+)/harvesting_journal/clean/$',
        views.clean_harvesting_journal,
        name='clean_harvesting_journal'
    ),
    url(
        '^sources/(?P<source_id>\d+)/indexing_rules/add/$',
        views.add_indexing_rule,
        name='add_indexing_rule'
    ),
    url(
        '^sources/(?P<source_id>\d+)/indexing_rules/(?P<id>\d+)/change/$',
        views.change_indexing_rule,
        name='change_indexing_rule'
    ),
    url(
        '^sources/(?P<source_id>\d+)/indexing_rules/(?P<id>\d+)/delete/$',
        views.delete_indexing_rule,
        name='delete_indexing_rule'
    ),
    url(
        '^sources/(?P<source_id>\d+)/indexing_journal/$',
        views.indexing_journal,
        name='indexing_journal'
    ),
    url(
        '^sources/(?P<source_id>\d+)/indexing_journal/clean/$',
        views.clean_indexing_journal,
        name='clean_indexing_journal'
    ),
    url('^index_transformation_rules/$', views.index_transformation_rules, name='index_transformation_rules'),
    url('^index_transformation_rules/add/$', views.add_index_transformation_rule, name='add_index_transformation_rule'),
    url(
        '^index_transformation_rules/(?P<id>\d+)/change/$',
        views.change_index_transformation_rule,
        name='change_index_transformation_rule'
    ),
    url(
        '^index_transformation_rules/(?P<id>\d+)/delete/$',
        views.delete_index_transformation_rule,
        name='delete_index_transformation_rule'
    ),

    url('^indexing_source/(?P<id>\d+)/$', views.index_source, name='index_source'),
    url('^reset_source_index/(?P<id>\d+)/$', views.reset_source_index, name='reset_source_index'),
    url('^clean_source_index/(?P<id>\d+)/$', views.clean_source_index, name='clean_source_index'),

    url('^records/$', views.records, name='records'),
    url('^records/(?P<source_id>\d+)/delete/$', views.delete_source_records, name='delete_source_records'),
    url('^records/(?P<source_id>\d+)/clean/$', views.clean_source_records, name='clean_source_records'),
    url('^records/(?P<source_id>\d+)/$', views.records, name='source_records'),
    url('^record/$', views.record, name='record'),
    url('^record/(?P<source_id>\d+)/$', views.record, name='source_record'),

]
