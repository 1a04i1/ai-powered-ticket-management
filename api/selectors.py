from rest_framework.exceptions import PermissionDenied

from api.models import CompanyMembership


def get_active_membership(user, company_id):
    """Return the active membership for a user in a company, or None."""
    if not user or not user.is_authenticated or company_id is None:
        return None

    return (
        CompanyMembership.objects.select_related("company", "role")
        .filter(
            user=user,
            company_id=company_id,
            company__is_active=True,
            is_active=True,
        )
        .first()
    )


def company_scoped_queryset(queryset, user, company_id):
    """
    Restrict a company-owned queryset to one tenant.

    Use this in every list/detail selector for tenant-owned resources.
    The model must have a company_id field. A platform superuser bypasses
    membership checks, but the queryset remains restricted to company_id.
    """
    if company_id is None:
        raise PermissionDenied("A company context is required.")

    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required.")

    if user.is_superuser:
        return queryset.filter(company_id=company_id)

    if get_active_membership(user, company_id) is None:
        raise PermissionDenied("You are not an active member of this company.")

    return queryset.filter(company_id=company_id)
