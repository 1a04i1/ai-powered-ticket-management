from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.models import (
    Company,
    CompanyMembership,
    Permission,
    Role,
    RolePermission,
)
from api.selectors import get_active_membership


DEFAULT_PERMISSION_DEFINITIONS = [
    ("company.view", "View company"),
    ("company.update", "Update company"),
    ("members.view", "View company members"),
    ("members.manage", "Manage company members"),
    ("roles.view", "View roles"),
    ("roles.manage", "Manage roles"),
    ("tickets.view", "View tickets"),
    ("tickets.create", "Create tickets"),
    ("tickets.update", "Update tickets"),
    ("tickets.assign", "Assign tickets"),
    ("tickets.delete", "Delete tickets"),
    ("reports.view", "View reports"),
    ("settings.manage", "Manage company settings"),
]


DEFAULT_ROLE_PERMISSIONS = {
    "company_admin": [code for code, _ in DEFAULT_PERMISSION_DEFINITIONS],
    "manager": [
        "company.view", "members.view", "roles.view",
        "tickets.view", "tickets.create", "tickets.update",
        "tickets.assign", "reports.view",
    ],
    "agent": ["company.view", "tickets.view", "tickets.create", "tickets.update"],
    "customer": ["tickets.view", "tickets.create"],
}


@transaction.atomic
def create_company_with_admin(*, name, slug, admin_user):
    """Create a tenant, its standard roles/permissions, and the first admin membership."""
    if not admin_user or not admin_user.is_authenticated:
        raise PermissionDenied("An authenticated user is required.")

    company = Company.objects.create(name=name, slug=slug)

    permissions = {}
    for code, label in DEFAULT_PERMISSION_DEFINITIONS:
        permission, _ = Permission.objects.get_or_create(
            code=code,
            defaults={"name": label},
        )
        permissions[code] = permission

    roles = {}
    role_labels = {
        "company_admin": ("Company Admin", "Full company administration"),
        "manager": ("Manager", "Manage day-to-day ticket operations"),
        "agent": ("Agent", "Work on assigned tickets"),
        "customer": ("Customer", "Create and track own tickets"),
    }

    for role_slug, (role_name, description) in role_labels.items():
        role = Role.objects.create(
            company=company,
            name=role_name,
            slug=role_slug,
            description=description,
            is_system=True,
        )
        RolePermission.objects.bulk_create(
            [
                RolePermission(role=role, permission=permissions[code])
                for code in DEFAULT_ROLE_PERMISSIONS[role_slug]
            ]
        )
        roles[role_slug] = role

    CompanyMembership.objects.create(
        user=admin_user,
        company=company,
        role=roles["company_admin"],
    )
    return company


@transaction.atomic
def assign_company_role(*, actor, user, company_id, role_id):
    """Add/update a user's role only when the actor can manage members in that tenant."""
    if not actor or not actor.is_authenticated:
        raise PermissionDenied("Authentication is required.")

    if not actor.is_superuser:
        membership = get_active_membership(actor, company_id)
        if (
            membership is None
            or not membership.role.permissions.filter(code="members.manage").exists()
        ):
            raise PermissionDenied("You cannot manage members in this company.")

    try:
        role = Role.objects.get(pk=role_id, company_id=company_id)
        company = Company.objects.get(pk=company_id, is_active=True)
    except (Role.DoesNotExist, Company.DoesNotExist):
        raise ValidationError("The company or role does not exist.")

    membership, created = CompanyMembership.objects.update_or_create(
        user=user,
        company=company,
        defaults={"role": role, "is_active": True},
    )
    return membership, created
