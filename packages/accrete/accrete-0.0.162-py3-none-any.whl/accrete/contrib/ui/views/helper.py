from django.utils.translation import gettext_lazy as _
from django.apps import apps
from accrete.contrib.ui.response import WindowResponse, ModalResponse


def is_htmx(request):
    return request.headers.get('HX-Request', 'false') == 'true'


def get_group_data(tenant_groups, member_groups) -> dict:

    def _flat_groups() -> tuple[list[str], list[str]]:
        def group_list(g):
            if isinstance(g, str):
                return [g]
            elif isinstance(g, tuple):
                return [x for x in g]
            return []
        tenant_groups_res = []
        member_groups_res = []
        for group in tenant_groups:
            tenant_groups_res.extend(group_list(group))
        for group in member_groups:
            member_groups_res.extend(group_list(group))
        return tenant_groups_res, member_groups_res

    AccessGroup = apps.get_model('accrete', 'AccessGroup')
    data = {}
    flat_tenant_groups, flat_member_groups = _flat_groups()
    if flat_tenant_groups:
        data.update(tenant_groups=[])
        access_groups = AccessGroup.objects.filter(
            code__in=flat_tenant_groups,
            apply_on='tenant'
        ).all()
        group_data = {item[0]: item[1] for item in access_groups.values_list('code', 'name')}
        for group in tenant_groups:
            if isinstance(group, tuple):
                data['tenant_groups'].append(' & '.join([group_data.get(g, g) for g in group]))
            else:
                data['tenant_groups'].append(group_data.get(group, group))
    if flat_member_groups:
        data.update(member_groups=[])
        access_groups = AccessGroup.objects.filter(
            code__in=flat_member_groups,
            apply_on='member'
        ).all()
        group_data = {item[0]: item[1] for item in access_groups.values_list('code', 'name')}
        for group in member_groups:
            if isinstance(group, tuple):
                data['member_groups'].append(' & '.join([group_data.get(g, g) for g in group]))
            else:
                data['member_groups'].append(group_data.get(group, group))
    return data


def access_denied_page_response(request, group_data):
    return WindowResponse(
        title=str(_('Access Denied')),
        overview_template='mirox/base/group_not_set.html',
        context=dict(groups=group_data),
        is_centered=True
    ).response(request)


def access_denied_modal_response(request, group_data):
    res = ModalResponse(
        template='mirox/base/group_not_set_modal.html',
        title=str(_('Access Denied')),
        modal_id='group-missing-modal',
        context=dict(groups=group_data)
    ).response(request)
    res.headers['HX-Reswap'] = 'none'
    res.headers['HX-Push-Url'] = 'false'
    return res
