from functools import wraps
from typing import Callable
from django.http import HttpRequest
from accrete.decorator import tenant_required as tenant_required_base
from django.http import HttpResponse
from .helper import (
    is_htmx,
    get_group_data,
    access_denied_modal_response,
    access_denied_page_response
)


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

    def decorator(f):

        def handle_group_missing(request, tenant_groups, member_groups):
            tenant_groups = tenant_groups or []
            member_groups = member_groups or []
            if is_htmx(request):
                return access_denied_modal_response(
                    request, get_group_data(tenant_groups, member_groups)
                )
            return access_denied_page_response(
                request, get_group_data(tenant_groups, member_groups)
            )

        @wraps(f)
        @tenant_required_base(
            tenant_groups=tenant_groups,
            member_groups=member_groups,
            group_missing_action=group_missing_action or handle_group_missing,
            redirect_field_name=redirect_field_name,
            login_url=login_url
        )
        def _wrapped_view(request, *args, **kwargs):
            return f(request, *args, **kwargs)
        return _wrapped_view
    return decorator
