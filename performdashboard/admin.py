from django.contrib import admin
from .models import PerformanceCategory

# Register your models here.
class PerformanceCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('performance_name',)}
    list_display = ('performance_name', 'slug')

admin.site.register(PerformanceCategory, PerformanceCategoryAdmin)