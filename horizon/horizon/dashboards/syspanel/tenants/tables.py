import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import tables

from ..users.tables import UsersTable


LOG = logging.getLogger(__name__)


class ModifyQuotasLink(tables.LinkAction):
    name = "quotas"
    verbose_name = _("Modify Quotas")
    url = "horizon:syspanel:tenants:quotas"
    attrs = {"class": "ajax-modal"}


class ViewMembersLink(tables.LinkAction):
    name = "users"
    verbose_name = _("Modify Users")
    url = "horizon:syspanel:tenants:users"


class UsageLink(tables.LinkAction):
    name = "usage"
    verbose_name = _("View Usage")
    url = "horizon:syspanel:tenants:usage"


class EditLink(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Tenant")
    url = "horizon:syspanel:tenants:update"
    attrs = {"class": "ajax-modal"}


class CreateLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create New Tenant")
    url = "horizon:syspanel:tenants:create"
    attrs = {"class": "ajax-modal btn small"}


class DeleteTenantsAction(tables.DeleteAction):
    data_type_singular = _("Tenant")
    data_type_plural = _("Tenants")

    def delete(self, request, obj_id):
        api.keystone.tenant_delete(request, obj_id)


class TenantFilterAction(tables.FilterAction):
    def filter(self, table, tenants, filter_string):
        """ Really naive case-insensitive search. """
        # FIXME(gabriel): This should be smarter. Written for demo purposes.
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.name.lower():
                return True
            return False

        return filter(comp, tenants)


class TenantsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('Id'))
    name = tables.Column('name', verbose_name=_('Name'))
    description = tables.Column(lambda obj: getattr(obj, 'description', None),
                                verbose_name=_('Description'))
    enabled = tables.Column('enabled', verbose_name=_('Enabled'), status=True)

    class Meta:
        name = "tenants"
        verbose_name = _("Tenants")
        row_actions = (EditLink, UsageLink, ViewMembersLink, ModifyQuotasLink,
                       DeleteTenantsAction)
        table_actions = (TenantFilterAction, CreateLink, DeleteTenantsAction)


class RemoveUserAction(tables.BatchAction):
    name = "remove_user"
    action_present = _("Remove")
    action_past = _("Removed")
    data_type_singular = _("User")
    data_type_plural = _("Users")
    classes = ('danger',)

    def action(self, request, user_id):
        tenant_id = self.table.kwargs['tenant_id']
        api.keystone.remove_tenant_user(request, tenant_id, user_id)


class TenantUsersTable(UsersTable):
    class Meta:
        name = "tenant_users"
        verbose_name = _("Users For Tenant")
        table_actions = (RemoveUserAction,)
        row_actions = (RemoveUserAction,)


class AddUserAction(tables.LinkAction):
    name = "add_user"
    verbose_name = _("Add To Tenant")
    url = "horizon:syspanel:tenants:add_user"
    classes = ('ajax-modal',)

    def get_link_url(self, user):
        tenant_id = self.table.kwargs['tenant_id']
        return reverse(self.url, args=(tenant_id, user.id))


class AddUsersTable(UsersTable):
    class Meta:
        name = "add_users"
        verbose_name = _("Add New Users")
        table_actions = ()
        row_actions = (AddUserAction,)
