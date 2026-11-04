from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from types import SimpleNamespace

from api.models import CompanyMembership, Role
from api.permissions import HasCompanyPermission, IsCompanyAdmin, IsCompanyMember
from api.services.authorization_service import assign_company_role, create_company_with_admin

User = get_user_model()


class CompanyAuthorizationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(username="admin", password="test-pass-123")
        self.agent = User.objects.create_user(username="agent", password="test-pass-123")
        self.other = User.objects.create_user(username="other", password="test-pass-123")
        self.company = create_company_with_admin(
            name="Acme Support", slug="acme-support", admin_user=self.admin
        )
        self.agent_role = Role.objects.get(company=self.company, slug="agent")
        CompanyMembership.objects.create(
            user=self.agent, company=self.company, role=self.agent_role
        )

    def _request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def _view(self, company_id, required_permission=None):
        return SimpleNamespace(
            kwargs={"company_id": company_id},
            required_permission=required_permission,
        )

    def test_company_creation_creates_roles_and_admin_membership(self):
        membership = CompanyMembership.objects.get(user=self.admin, company=self.company)
        self.assertEqual(membership.role.slug, "company_admin")
        self.assertEqual(
            set(Role.objects.filter(company=self.company).values_list("slug", flat=True)),
            {"company_admin", "manager", "agent", "customer"},
        )

    def test_active_member_is_allowed(self):
        self.assertTrue(IsCompanyMember().has_permission(
            self._request(self.agent), self._view(self.company.id)
        ))

    def test_non_member_is_denied(self):
        self.assertFalse(IsCompanyMember().has_permission(
            self._request(self.other), self._view(self.company.id)
        ))

    def test_permission_code_is_enforced(self):
        self.assertTrue(HasCompanyPermission().has_permission(
            self._request(self.agent), self._view(self.company.id, "tickets.create")
        ))
        self.assertFalse(HasCompanyPermission().has_permission(
            self._request(self.agent), self._view(self.company.id, "members.manage")
        ))

    def test_company_admin_check(self):
        self.assertTrue(IsCompanyAdmin().has_permission(
            self._request(self.admin), self._view(self.company.id)
        ))
        self.assertFalse(IsCompanyAdmin().has_permission(
            self._request(self.agent), self._view(self.company.id)
        ))

    def test_member_assignment_requires_management_permission(self):
        new_user = User.objects.create_user(username="new-agent", password="test-pass-123")
        with self.assertRaises(Exception):
            assign_company_role(
                actor=self.agent, user=new_user,
                company_id=self.company.id, role_id=self.agent_role.id,
            )
        membership, created = assign_company_role(
            actor=self.admin, user=new_user,
            company_id=self.company.id, role_id=self.agent_role.id,
        )
        self.assertTrue(created)
        self.assertEqual(membership.role_id, self.agent_role.id)

    def test_role_from_another_company_cannot_be_assigned(self):
        another_company = create_company_with_admin(
            name="Other Co", slug="other-co", admin_user=self.other
        )
        other_role = Role.objects.get(company=another_company, slug="agent")
        with self.assertRaises(Exception):
            assign_company_role(
                actor=self.admin, user=self.other,
                company_id=self.company.id, role_id=other_role.id,
            )
