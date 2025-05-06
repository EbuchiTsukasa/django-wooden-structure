from django.contrib import admin

from .models import Unit, OrgChart, Closure

# Register your models here.

admin.site.register(Unit)

@admin.register(OrgChart)
class OrgChartAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role')

@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = ('display_str', 'depth')
    ordering = ('depth', 'parent')

    def display_str(self, obj):
        return str(obj)
    display_str.short_description = '親-子'