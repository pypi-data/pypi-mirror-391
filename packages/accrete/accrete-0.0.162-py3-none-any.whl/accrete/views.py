import os

from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, get_object_or_404, resolve_url
from django.conf import settings
from accrete.models import Tenant, Member
from accrete.tenant import get_tenant, tenant_has_group, member_has_group
from accrete import config
from accrete.decorator import tenant_required


class TenantRequiredMixin(LoginRequiredMixin):

    # Redirect to the specified url if the group check fails
    TENANT_NOT_SET_URL = None
    GROUP_NOT_SET_URL = None

    # If set, one of the supplied groups must be set on the
    # tenant and member respectively. If the list item is a tuple,
    # all the groups in the tuple must be set.
    TENANT_GROUPS: list[str | tuple[str]] = []
    MEMBER_GROUPS: list[str | tuple[str]] = []

    def dispatch(self, request, *args, **kwargs):
        if not self.get_tenant():
            return self.handle_tenant_not_set()
        if self.request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not self.check_tenant_group():
            return self.handle_tenant_group_not_set()
        if not self.check_member_group():
            return self.handle_member_group_not_set()
        return super().dispatch(request, *args, **kwargs)

    def handle_tenant_not_set(self):
        return redirect(
            resolve_url(self.get_tenant_not_set_url())
            + f'?next={self.request.get_full_path_info()}'
        )

    def handle_tenant_group_not_set(self):
        return redirect(self.get_group_not_set_url())

    def handle_member_group_not_set(self):
        return redirect(self.get_group_not_set_url())

    def get_tenant_not_set_url(self):
        tenant_not_set_url = (
            self.TENANT_NOT_SET_URL
            or config.ACCRETE_TENANT_NOT_SET_URL
        )
        if not tenant_not_set_url:
            cls_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f"{cls_name} is missing the tenant_not_set_url attribute. "
                f"Define {cls_name}.TENANT_NOT_SET_URL, "
                f"settings.ACCRETE_TENANT_NOT_SET_URL, or override "
                f"{cls_name}.get_tenant_not_set_url()."
            )
        return tenant_not_set_url

    def get_group_not_set_url(self):
        group_not_set_url = (
            self.GROUP_NOT_SET_URL
            or config.ACCRETE_GROUP_NOT_SET_URL
        )
        if not group_not_set_url:
            cls_name = self.__class__.__name__
            raise ImproperlyConfigured(
                f"{cls_name} is missing the group_not_set_url attribute. "
                f"Define {cls_name}.GROUP_NOT_SET_URL, "
                f"settings.ACCRETE_GROUP_NOT_SET_URL, or override "
                f"{cls_name}.get_group_not_set_url()."
            )
        return group_not_set_url

    def check_tenant_group(self) -> bool:
        if not self.TENANT_GROUPS:
            return True
        for group in self.TENANT_GROUPS:
            if isinstance(group, tuple) and all([tenant_has_group(g) for g in group]):
                return True
            elif tenant_has_group(group):
                return True
        return False

    def check_member_group(self) -> bool:
        if not self.MEMBER_GROUPS:
            return True
        for group in self.MEMBER_GROUPS:
            if isinstance(group, tuple) and all([member_has_group(g) for g in group]):
                return True
            elif member_has_group(group):
                return True
        return False

    @staticmethod
    def get_tenant():
        return get_tenant()


@tenant_required()
def get_tenant_file(request, tenant_id, filepath):
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    if not request.user.is_staff:
        member = Member.objects.filter(user=request.user, tenant=tenant)
        if not member.exists():
            return HttpResponseNotFound()
    filepath = f'{settings.MEDIA_ROOT}/{tenant_id}/{filepath}'
    if not os.path.exists(filepath):
        return HttpResponseNotFound()
    with open(filepath, 'rb') as f:
        return HttpResponse(f)
