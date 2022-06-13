from django.contrib import admin
from .models import Workflow

# Register your models here.
class WorkflowAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

admin.site.register(Workflow, WorkflowAdmin)