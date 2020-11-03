from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Сustomer, Order, Profile, Сompany, Integration,\
    Lead, LeadStatus, CompanyLeadStatus
from django.contrib.auth.models import User


class UserProfileInline(admin.StackedInline):
    model = Profile


class UserIntegrationInline(admin.StackedInline):
    model = Integration


class NewUserAdmin(UserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
admin.site.register(Сustomer)
admin.site.register(Order)
admin.site.register(Сompany)
admin.site.register(Lead)
admin.site.register(LeadStatus)
admin.site.register(CompanyLeadStatus)
admin.site.register(Integration)
