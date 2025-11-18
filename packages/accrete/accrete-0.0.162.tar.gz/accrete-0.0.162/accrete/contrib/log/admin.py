from django.contrib import admin
from . import models


class LogConfigFieldInLine(admin.TabularInline):

    model = models.LogConfigField


class LogConfigAdmin(admin.ModelAdmin):

    model = models.LogConfig
    list_display = ('model', 'ignore_errors', 'exclude_fields')
    search_fields = ('pk', 'model')
    list_filter = ['ignore_errors', 'exclude_fields']
    inlines = [LogConfigFieldInLine]


class LogAdmin(admin.ModelAdmin):

    model = models.LogConfig
    list_display = (
        'model', 'field', 'object_id', 'log_date', 'old_value', 'new_value',
        'activity', 'user', 'tenant'
    )
    search_fields = ('model', 'field', 'object_id', 'old_value')
    list_filter = ['model', 'tenant']


class ActivityLogInline(admin.TabularInline):

    model = models.Log
    extra = 0


class ActivityAdmin(admin.ModelAdmin):

    model = models.Activity
    list_display = ('code', 'description', 'model', 'object_id', 'user', 'tenant')
    search_fields = ['code', 'description', 'model', 'object_id']
    list_filter = ['code', 'tenant']
    inlines = [ActivityLogInline]


admin.site.register(models.LogConfig, LogConfigAdmin)
admin.site.register(models.Log, LogAdmin)
admin.site.register(models.Activity, ActivityAdmin)
