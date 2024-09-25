from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AttendanceRecord, CustomUser, Result, Routine, StudentClass, Subject, Teacher, Student, Notes, Notice
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Teacher, Student

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher', 'is_student')}),
    )

    # Restrict the queryset so that only superusers can view teachers
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return queryset
    #     # Staff users can only see non-teacher users
    #     return queryset.filter(is_teacher=False)

    # # Restrict view permission so that only superusers can view Teacher users
    # def has_view_permission(self, request, obj=None):
    #     if obj and obj.is_teacher and not request.user.is_superuser:
    #         return False  # Only superusers can view teacher users
    #     return super().has_view_permission(request, obj)

    # # Allow only superusers to add users, and staff can add only students
    # def has_add_permission(self, request):
    #     if request.user.is_superuser:
    #         return True
    #     return request.user.is_staff and not request.user.is_teacher

    # # Superusers can change both teachers and students; staff can only change students
    # def has_change_permission(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     if obj and obj.is_student and request.user.is_staff:
    #         return True
    #     return False

    # # Superusers can delete both; staff can delete only students
    # def has_delete_permission(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return True
    #     if obj and obj.is_student and request.user.is_staff:
    #         return True
    #     return False

    # # Control password change permission based on user role
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if not request.user.is_superuser:
    #         # Remove the password field for staff users if they shouldn't change passwords
    #         form.base_fields.pop('password', None)
    #     return form





class TeacherAdmin(admin.ModelAdmin):
    # Restrict adding, changing, and deleting teachers to superusers only
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class StudentAdmin(admin.ModelAdmin):
    # Allow staff to add, change, and delete students
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


# Register models with their respective admin classes
# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Teacher, TeacherAdmin)
# admin.site.register(Student, StudentAdmin)



admin.site.register(Teacher, TeacherAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(StudentClass)
admin.site.register(Result)
admin.site.register(Notes)
admin.site.register(Notice)
admin.site.register(Subject)
admin.site.register(Routine)
admin.site.register(AttendanceRecord)

