# Generated for the company-scoped RBAC authorization module.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0002_alter_socialaccount_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(max_length=160, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "companies", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("description", models.TextField(blank=True)),
            ],
            options={"db_table": "permissions", "ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_system", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="api.company")),
                ("permissions", models.ManyToManyField(blank=True, related_name="roles", through="api.RolePermission", to="api.permission")),
            ],
            options={
                "db_table": "roles",
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(fields=("company", "slug"), name="unique_role_slug_per_company"),
                ],
            },
        ),
        migrations.CreateModel(
            name="RolePermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("permission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_permissions", to="api.permission")),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_permissions", to="api.role")),
            ],
            options={
                "db_table": "role_permissions",
                "constraints": [
                    models.UniqueConstraint(fields=("role", "permission"), name="unique_permission_per_role"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CompanyMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="api.company")),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="api.role")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="company_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "company_memberships",
                "constraints": [
                    models.UniqueConstraint(fields=("user", "company"), name="unique_user_membership_per_company"),
                ],
                "indexes": [
                    models.Index(fields=["company", "is_active"], name="company_mem_company_2d92a0_idx"),
                    models.Index(fields=["user", "is_active"], name="company_mem_user_id_7f36f4_idx"),
                ],
            },
        ),
    ]
