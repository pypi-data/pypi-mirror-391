from django.urls import path

from .views import filter

app_name = 'ui'

urlpatterns = [
    path('filter/<str:model>/params/', filter.params, name='filter_params'),
    path('filter/<str:model>/input/', filter.set_filter_input, name='filter_input'),
    path('filter/<str:model>/query/add/', filter.filter_add_query, name='filter_add_query')
]
