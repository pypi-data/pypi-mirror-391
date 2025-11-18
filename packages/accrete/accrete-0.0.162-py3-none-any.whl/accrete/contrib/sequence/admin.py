from django.contrib import admin
from .models import Sequence


class SequenceAdmin(admin.ModelAdmin):
    model = Sequence
    list_display = ('name', 'nextval', 'step', 'tenant')
    search_fields = ('name', 'tenant__name')
    list_filter = ['tenant']


admin.site.register(Sequence, SequenceAdmin)
