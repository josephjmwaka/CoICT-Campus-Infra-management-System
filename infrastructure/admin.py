from django.contrib import admin
from .models import IssueReport

class IssueReportAdmin(admin.ModelAdmin):
    list_display = ('reported_by', 'block_number', 'floor_number', 'room_number', 'equipment_name', 'problem_description', 'status', 'created_at', 'image')
    list_filter = ('status', 'equipment_name', 'created_at')
    search_fields = ('room_number', 'block_number', 'user__username')
    ordering = ('-created_at',)

admin.site.register(IssueReport, IssueReportAdmin)
