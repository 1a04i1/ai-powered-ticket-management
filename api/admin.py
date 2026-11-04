from django.contrib import admin

from api.models import (
    Company,
    CompanyMembership,
    Permission,
    Role,
    RolePermission,
    SocialAccount,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "slug", "is_system")
    list_filter = ("company", "is_system")
    search_fields = ("name", "slug", "company__name")
    inlines = (RolePermissionInline,)


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "is_active", "joined_at")
    list_filter = ("company", "role", "is_active")
    search_fields = ("user__username", "user__email", "company__name")


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "email", "created_at")
    search_fields = ("user__username", "email", "provider_user_id")
