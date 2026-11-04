from rest_framework.permissions import BasePermission

from api.models import CompanyMembership


def _company_id_from_view(request, view):
    company_id = view.kwargs.get("company_id")
    if company_id is None:
        company_id = getattr(view, "company_id", None)
    return company_id


def _active_membership(user, company_id):
    if not getattr(user, "is_authenticated", False) or company_id is None:
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


class IsCompanyMember(BasePermission):
    """Allow active members of the company in the URL/view context."""

    message = "You are not an active member of this company."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        company_id = _company_id_from_view(request, view)
        return _active_membership(request.user, company_id) is not None


class HasCompanyPermission(BasePermission):
    """
    Enforce a permission code declared on the view:
        required_permission = "tickets.create"

    The company context must come from the URL kwarg company_id or the
    view's company_id attribute. Do not take tenant identity from request data.
    """

    message = "You do not have permission to perform this action in this company."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        permission_code = getattr(view, "required_permission", None)
        company_id = _company_id_from_view(request, view)
        if not permission_code or company_id is None:
            return False

        membership = _active_membership(user, company_id)
        if membership is None:
            return False

        return membership.role.permissions.filter(code=permission_code).exists()


class IsCompanyAdmin(BasePermission):
    """Allow company admins and Django platform superusers."""

    message = "Company administrator access is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        company_id = _company_id_from_view(request, view)
        membership = _active_membership(user, company_id)
        return bool(membership and membership.role.slug == "company_admin")
