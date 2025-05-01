from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from infrastructure.admin import custom_admin_site

# Option 1: Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Option 2: Custom UserAdmin that includes the inline
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number', 'get_department')
    list_select_related = ('profile', )

    def get_phone_number(self, instance):
        return instance.profile.phone_number
    get_phone_number.short_description = 'Phone Number'

    def get_department(self, instance):
        return instance.profile.department
    get_department.short_description = 'Department'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


custom_admin_site.register(User, CustomUserAdmin)  # Register User with our custom admin

# register UserProfile separately for direct access
@admin.register(UserProfile, site=custom_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'department')
    search_fields = ('user__username', 'phone_number', 'department')