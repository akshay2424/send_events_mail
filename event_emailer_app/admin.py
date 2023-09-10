from django.contrib import admin
from .models import Employee, EmailTemplate

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'dob')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'subject')
    search_fields = ('event_type', 'subject')

