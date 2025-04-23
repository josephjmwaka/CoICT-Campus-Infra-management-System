from django.contrib import admin
from .models import (
    Block, Floor, Room, 
    EquipmentCategory, Equipment,
    Generator, MaintenanceRequest,
    MaintenanceLog
)
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

# Inline Admin Classes
class FloorInline(admin.TabularInline):
    model = Floor
    extra = 0
    fields = ['number', 'name']
    show_change_link = True

class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ['number', 'name', 'room_type']
    show_change_link = True
    readonly_fields = ['is_generator_room']

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 0
    fields = ['name', 'model_number', 'status']
    show_change_link = True

class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    readonly_fields = ['completion_date']
    fields = ['technician', 'action_taken', 'completion_date']

# Main Admin Classes
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'has_multiple_floors', 'room_count']
    list_filter = ['has_multiple_floors']
    search_fields = ['code', 'name']
    inlines = [FloorInline, RoomInline]
    
    def room_count(self, obj):
        return obj.rooms.count()
    room_count.short_description = "Rooms"

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['block', 'number', 'name']
    list_filter = ['block']
    search_fields = ['block__code', 'number', 'name']
    ordering = ['block', 'number']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['block', 'floor_display', 'number', 'name', 'room_type', 'is_generator_room']
    list_filter = ['block', 'room_type', 'is_generator_room']
    search_fields = ['block__code', 'number', 'name']
    inlines = [EquipmentInline]
    
    def floor_display(self, obj):
        return obj.floor.number if obj.floor else "-"
    floor_display.short_description = "Floor"

@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'maintenance_interval', 'equipment_count']
    search_fields = ['name']
    
    def equipment_count(self, obj):
        return obj.equipment.count()
    equipment_count.short_description = "Equipment Count"

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_location', 'category', 'status', 'last_maintenance']
    list_filter = ['category', 'status', 'room__block']
    search_fields = ['name', 'model_number', 'serial_number']
    list_select_related = ['category', 'room', 'room__block']
    # readonly_fields = ['equipment_image']
    
    def room_location(self, obj):
        return f"{obj.room.block.code}{obj.room.number}"
    room_location.short_description = "Location"
    room_location.admin_order_field = 'room__number'
    
    # def equipment_image(self, obj):
    #     if obj.image:
    #         return format_html('<img src="{}" width="150" />', obj.image.url)
    #     return "-"
    # equipment_image.short_description = "Image Preview"

@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ['room_location', 'capacity_kva', 'fuel_type', 'next_service']
    list_filter = ['fuel_type']
    search_fields = ['room__block__code', 'room__number']
    
    def room_location(self, obj):
        return f"{obj.room.block.code}{obj.room.number}"
    room_location.short_description = "Location"

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'reported_by', 'short_problem', 'location', 
        'issue_type', 'priority', 'status', 
         'created_at', 'image'
    ]
    list_filter = ['status', 'priority', 'issue_type', 'block']
    search_fields = ['problem', 'description', 'room__number']
    list_select_related = ['block', 'floor', 'room', 'reported_by']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MaintenanceLogInline]
    actions = ['mark_as_completed', 'mark_as_in_progress']
    date_hierarchy = 'created_at'
    
    def short_problem(self, obj):
        return obj.problem[:50] + "..." if len(obj.problem) > 50 else obj.problem
    short_problem.short_description = "Problem"
    
    def location(self, obj):
        parts = [f"Block {obj.block.code}"]
        # if obj.floor:
        #     parts.append(f"Floor {obj.floor.number}")
        if obj.room:
            parts.append(f"Room {obj.room.number}")
        return " ".join(parts)
    location.short_description = "Location"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f"{updated} requests marked as completed.")
    mark_as_completed.short_description = "Mark selected as completed"
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f"{updated} requests marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected as in progress"

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['request_link', 'technician', 'completion_date', 'labor_hours']
    list_filter = ['technician', 'completion_date']
    search_fields = ['request__problem', 'action_taken']
    readonly_fields = ['completion_date']
    
    def request_link(self, obj):
        url = reverse('admin:infrastructure_maintenancerequest_change', args=[obj.request.id])
        return mark_safe(f'<a href="{url}">{obj.request.problem}</a>')
    request_link.short_description = "Maintenance Request"