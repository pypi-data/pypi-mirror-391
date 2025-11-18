from functools import wraps
from typing import Callable
from django.shortcuts import redirect
from accrete import config
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest
from accrete.tenant import tenant_has_group, member_has_group


def tenant_required(
    tenant_groups: list[str | tuple[str, ...]] = None,
    member_groups: list[str | tuple[str, ...]] = None,
    group_missing_action: str | Callable[
        [HttpRequest, list[str | tuple[str]], list[str | tuple[str]]],
        HttpResponse
    ] = None,
    redirect_field_name: str = None,
    login_url: str = None
):
    from django.contrib.auth.views import login_required

    def decorator(f):
        @wraps(f)
        @login_required(
            redirect_field_name=redirect_field_name,
            login_url=login_url
        )
        def _wrapped_view(request, *args, **kwargs):

            def handle_group_missing():
                if callable(group_missing_action):
                    return group_missing_action(
                        request, tenant_groups, member_groups
                    )
                return (
                    redirect(config.ACCRETE_GROUP_NOT_SET_URL)
                    if config.ACCRETE_GROUP_NOT_SET_URL
                    else HttpResponseForbidden()
                )

            tenant = request.tenant
            if not tenant:
                return redirect(config.ACCRETE_TENANT_NOT_SET_URL)
            for tenant_group in (tenant_groups or []):
                if isinstance(tenant_group, tuple) and all([
                    tenant_has_group(g) for g in tenant_group
                ]):
                    break
                elif isinstance(tenant_group, str) and tenant_has_group(tenant_group):
                    break
                return handle_group_missing()
            for member_group in (member_groups or []):
                if isinstance(member_group, tuple) and all([
                    member_has_group(g) for g in member_group
                ]):
                    break
                elif isinstance(member_group, str) and member_has_group(member_group):
                    break
                return handle_group_missing()
            return f(request, *args, **kwargs)
        return _wrapped_view
    return decorator
