import json
import contextvars

from django.db import models
from django.db.models.query import RawQuerySet
from django.apps import apps

from accrete.fields import TranslatedCharField, TranslatedTextField
from accrete.utils.models import model_to_dict
from accrete.tenant import get_tenant, get_member

activity_contextvar = contextvars.ContextVar('activity', default=None)

TYPES_FK = ['AutoField', 'BigAutoField', 'ForeignKey']
TYPES_INT = ['IntegerField', 'PositiveSmallIntegerField']
TYPES_DECIMAL = ['DecimalField']
TYPES_FLOAT = ['FloatField']
TYPES_STR = ['CharField', 'TextField']
TYPES_BOOL = ['BooleanField']
TYPES_DATETIME = ['DateTimeField']
TYPES_DATE = ['DateField']
TYPES_TIME = ['TimeField']
TYPES_JSON = ['JSONField']


class ActivityContext:

    def __init__(
        self,
        code: str, *,
        description: str | dict = None,
        instance: models.Model = None
    ):
        self.code = code
        self.description = description
        self.instance = instance
        tenant = get_tenant()
        member = get_member()
        Activity = apps.get_model('log', 'Activity')
        self.activity = Activity(
            code=code,
            description=self.description,
            tenant=tenant,
            user=member and member.user
        )
        self.set_instance(self.instance)
        self.activity.save()

    def __enter__(self):
        set_activity(self.activity)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_activity(None)

    def set_instance(self, instance):
        self.instance = instance
        self.activity.model = (
            self.instance
            and f'{self.instance._meta.app_label}.{self.instance._meta.model_name}'
            or None
        )
        self.activity.object_id = self.instance and self.instance.pk or None
        self.activity.save()


def set_activity(activity_instance):
    activity_contextvar.set(activity_instance)


def get_activity():
    return activity_contextvar.get()


def activity(
    code: str, *,
    description: str | dict = None,
    instance: models.Model = None
):
    return ActivityContext(
        code=code,
        description=description,
        instance=instance
    )


def internal_type_to_log_type(field: models.Field):
    internal_type = field.get_internal_type()
    if internal_type in TYPES_FK:
        return 'fk'
    if internal_type in TYPES_INT:
        return 'int'
    if internal_type in TYPES_FLOAT:
        return 'float'
    if internal_type in TYPES_DECIMAL:
        return 'decimal'
    if internal_type in TYPES_BOOL:
        return 'bool'
    if internal_type in TYPES_STR:
        return 'str'
    if internal_type in TYPES_DATE:
        return 'date'
    if internal_type in TYPES_DATETIME:
        return 'datetime'
    if internal_type in TYPES_JSON:
        return 'json'


def log_state_to_dict(logs: RawQuerySet) -> tuple[dict, dict]:
    state = dict()
    info = dict()
    if not logs:
        return state, info
    for log in logs:
        state.update({log.field: log.cast_value()})
        info.update({log.field: {'new_value_type': log.new_value_type}})
    return state, info


def log_value_to_instance_value(log) -> bool | int | None:
    if log.new_value_type == 'bool':
        return bool(log.new_value == 'True')

    if log.new_value == '':
        return None
    if log.new_value_type in ['fk', 'int']:
        return int(log.new_value)


def get_instance_state(instance: models.Model):
    LogConfig = apps.get_model('log', 'LogConfig')
    state = model_to_dict(instance)
    cleaned_state = dict()
    log_config = LogConfig.objects.filter(
        model=f'{instance._meta.app_label}.{instance._meta.model_name}'
    ).prefetch_related('fields').first()
    if not log_config:
        return cleaned_state
    all_fields = list(map(lambda x: x.name, instance._meta.get_fields()))
    if log_config.exclude_fields:
        fields_to_log = list(set(all_fields).difference(
            set(log_config.fields.all().values_list('field_name', flat=True))
        ))
    else:
        fields_to_log = log_config.fields.all().values_list(
            'field_name', flat=True
        )

    for f, v in state.items():
        if isinstance(v, (list, tuple)):
            continue
        if f not in fields_to_log:
            continue
        if (
            isinstance(v, dict)
            and isinstance(instance._meta.get_field(f), (TranslatedCharField, TranslatedTextField))
        ):
            cleaned_state.update({f: json.dumps(v)})
            continue
        cleaned_state.update({f: v})
    return cleaned_state
