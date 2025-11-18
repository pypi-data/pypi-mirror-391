from django.views.generic import View
from accrete.views import TenantRequiredMixin
from .helper import is_htmx, get_group_data, access_denied_modal_response, access_denied_page_response


class TenantView(TenantRequiredMixin, View):

    """
    Base View that handles displaying access denied messages
    to the user if member/tenant groups are missing.
    """

    def handle_tenant_group_not_set(self):
        if is_htmx(self.request):
            return access_denied_modal_response(self.request, get_group_data(self.TENANT_GROUPS, self.MEMBER_GROUPS))
        return access_denied_page_response(self.request, get_group_data(self.TENANT_GROUPS, self.MEMBER_GROUPS))

    def handle_member_group_not_set(self):
        if is_htmx(self.request):
            return access_denied_modal_response(self.request, get_group_data(self.TENANT_GROUPS, self.MEMBER_GROUPS))
        return access_denied_page_response(self.request, get_group_data(self.TENANT_GROUPS, self.MEMBER_GROUPS))
